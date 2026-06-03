"""Asset metadata sidecar.

Stores per-file metadata (tags, uploaded_by, uploaded_at, notes) alongside the
filesystem-native asset directory. One JSON file per artist at
`artists/<slug>/assets/assets.meta.json`, protected by flock so the admin UI
and the public intake portal can write concurrently without corrupting it.

Schema:
    {
      "labels": {
        "Sculpture": {"color": "#e07a5f", "created_at": 1779800000},
        ...
      },
      "files": {
        "<rel_path>": {
          "labels": ["Sculpture", "2024"],
          "uploaded_by": "intake:lydialott" | "admin",
          "uploaded_at": 1779800000,
          "notes": "Free-text"
        },
        ...
        "link:<hex>": {
          "kind": "link",
          "url": "https://…",
          "title": "Page title",
          "labels": [...], "notes": "…",
          "uploaded_by": ..., "uploaded_at": ...
        },
        ...
      }
    }

Link assets are metadata-only entries living in the same `files` dict, keyed
`link:<hex>` and carrying `kind: "link"`. They have no file on disk, so the
label/notes/delete helpers (which operate on arbitrary string keys) apply to
them unchanged; only directory-walking listers need to emit them separately.

The legacy field name was `tags`; reads coerce it to `labels` so older sidecars
keep working without a one-shot migration.

Paths are relative to the artist's `assets/` directory and always use forward
slashes (POSIX style), regardless of host OS.
"""
import json
import fcntl
import time
import secrets
from contextlib import contextmanager
from pathlib import Path


def _meta_path(artist_slug):
    return Path(f'artists/{artist_slug}/assets/assets.meta.json')


@contextmanager
def _locked(path, mode='r+'):
    """Open `path` with an exclusive flock. Caller can read+write the file
    inside the with-block; lock releases on exit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({'files': {}}, indent=2))
    f = open(path, mode)
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield f
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


def load_meta(artist_slug):
    """Return the metadata dict (or an empty one if no sidecar yet).
    Coerces legacy `tags` per-file to `labels`."""
    path = _meta_path(artist_slug)
    if not path.exists():
        return {'labels': {}, 'files': {}}
    try:
        with open(path) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except (json.JSONDecodeError, OSError):
        return {'labels': {}, 'files': {}}
    data.setdefault('labels', {})
    files = data.setdefault('files', {})
    for entry in files.values():
        if 'tags' in entry and 'labels' not in entry:
            entry['labels'] = entry.pop('tags')
    return data


def get_for(artist_slug, rel_path):
    """Return the metadata entry for one file, or None."""
    return load_meta(artist_slug).get('files', {}).get(_norm(rel_path))


def update_for(artist_slug, rel_path, **fields):
    """Merge `fields` into one file's metadata entry. Creates the entry if
    missing. Aliased: `tags` is rewritten to `labels`."""
    rel_path = _norm(rel_path)
    if 'tags' in fields and 'labels' not in fields:
        fields['labels'] = fields.pop('tags')
    path = _meta_path(artist_slug)
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {'labels': {}, 'files': {}}
        data.setdefault('labels', {})
        files = data.setdefault('files', {})
        entry = files.setdefault(rel_path, {})
        entry.update({k: v for k, v in fields.items() if v is not None})
        entry.setdefault('uploaded_at', int(time.time()))
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)
    return entry


def delete_for(artist_slug, rel_path):
    """Remove a single file's metadata. No-op if absent."""
    rel_path = _norm(rel_path)
    path = _meta_path(artist_slug)
    if not path.exists():
        return
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
        if rel_path in data.get('files', {}):
            del data['files'][rel_path]
            f.seek(0); f.truncate()
            json.dump(data, f, indent=2)


def rename_for(artist_slug, old_path, new_path):
    """Move a file's metadata entry from old_path to new_path. No-op if absent."""
    old_path = _norm(old_path)
    new_path = _norm(new_path)
    if old_path == new_path:
        return
    path = _meta_path(artist_slug)
    if not path.exists():
        return
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
        files = data.get('files', {})
        if old_path in files:
            files[new_path] = files.pop(old_path)
            f.seek(0); f.truncate()
            json.dump(data, f, indent=2)


def all_labels(artist_slug):
    """Return list of {name, color, count} for all known labels."""
    data = load_meta(artist_slug)
    labels = dict(data.get('labels', {}))
    counts = {}
    for entry in data.get('files', {}).values():
        for name in entry.get('labels') or []:
            counts[name] = counts.get(name, 0) + 1
            # Stray label only seen on files — register it with a fallback colour.
            if name not in labels:
                labels[name] = {'color': _next_colour(labels)}
    return [
        {'name': name, 'color': info.get('color') or _next_colour(labels), 'count': counts.get(name, 0)}
        for name, info in sorted(labels.items())
    ]


def create_label(artist_slug, name, color=None):
    """Register a label. Returns {name, color}. Picks a colour from the
    palette if none given. Idempotent: re-creating updates the colour."""
    name = (name or '').strip()
    if not name:
        raise ValueError('Label name required')
    if len(name) > 60:
        name = name[:60]
    path = _meta_path(artist_slug)
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {'labels': {}, 'files': {}}
        labels = data.setdefault('labels', {})
        if name in labels and not color:
            return {'name': name, **labels[name]}
        labels[name] = {
            'color': color or _next_colour(labels),
            'created_at': int(time.time()),
        }
        f.seek(0); f.truncate()
        json.dump(data, f, indent=2)
    return {'name': name, **labels[name]}


def delete_label(artist_slug, name):
    """Remove a label definition and strip it from every file's labels."""
    name = (name or '').strip()
    if not name:
        return
    path = _meta_path(artist_slug)
    if not path.exists():
        return
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
        labels = data.setdefault('labels', {})
        labels.pop(name, None)
        for entry in data.get('files', {}).values():
            if name in (entry.get('labels') or []):
                entry['labels'] = [n for n in entry['labels'] if n != name]
        f.seek(0); f.truncate()
        json.dump(data, f, indent=2)


def toggle_labels(artist_slug, paths, label, on=True):
    """Add (on=True) or remove (on=False) a label from multiple files. Used
    by bulk-label endpoint."""
    label = (label or '').strip()
    if not label or not paths:
        return
    paths = {_norm(p) for p in paths}
    path = _meta_path(artist_slug)
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {'labels': {}, 'files': {}}
        files = data.setdefault('files', {})
        # Ensure the label is registered (so it shows up in the bar even
        # before files reference it).
        labels = data.setdefault('labels', {})
        if label not in labels:
            labels[label] = {'color': _next_colour(labels), 'created_at': int(time.time())}
        for p in paths:
            entry = files.setdefault(p, {})
            current = list(entry.get('labels') or [])
            if on:
                if label not in current:
                    current.append(label)
            else:
                current = [n for n in current if n != label]
            entry['labels'] = current
        f.seek(0); f.truncate()
        json.dump(data, f, indent=2)


# Sticker palette — soft, slightly-desaturated paper-sticker tones.
_PALETTE = [
    '#e07a5f', '#81b29a', '#f2cc8f', '#3d5a80', '#9b5de5',
    '#f15bb5', '#00bbf9', '#90be6d', '#f9844a', '#577590',
    '#a4133c', '#b08968',
]


def _next_colour(existing_labels):
    """Pick the next palette colour the artist hasn't used yet; cycle once full."""
    used = {info.get('color') for info in existing_labels.values()}
    for c in _PALETTE:
        if c not in used:
            return c
    # All used — random from palette anyway.
    import random
    return random.choice(_PALETTE)


def all_tags(artist_slug):
    """Back-compat alias — returns just label names."""
    return [l['name'] for l in all_labels(artist_slug)]


# ── Link assets (metadata-only, no file on disk) ──────────────────────────

def is_link_key(key):
    """True if `key` names a link asset rather than a real file path."""
    return str(key).startswith('link:')


def add_link(artist_slug, url, title=None, notes=None, labels=None,
             uploaded_by='admin'):
    """Register a link as a metadata-only asset under a `link:<hex>` key.
    Returns the new entry as {path, ...fields}. Stored in the same `files`
    dict as real uploads so labelling/notes/delete flow through unchanged."""
    url = (url or '').strip()
    if not url:
        raise ValueError('URL required')
    key = f'link:{secrets.token_hex(6)}'
    entry = {
        'kind': 'link',
        'url': url[:2000],
        'uploaded_by': uploaded_by,
        'uploaded_at': int(time.time()),
    }
    if title:
        entry['title'] = str(title)[:300]
    if notes:
        entry['notes'] = str(notes)[:2000]
    if labels:
        entry['labels'] = list(labels)
    path = _meta_path(artist_slug)
    with _locked(path) as f:
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {'labels': {}, 'files': {}}
        data.setdefault('labels', {})
        data.setdefault('files', {})[key] = entry
        f.seek(0); f.truncate()
        json.dump(data, f, indent=2)
    return {'path': key, **entry}


def links_for(artist_slug):
    """Return [{path, ...entry}] for every link asset, newest first."""
    files = load_meta(artist_slug).get('files', {})
    out = [{'path': k, **v} for k, v in files.items() if v.get('kind') == 'link']
    out.sort(key=lambda e: -(e.get('uploaded_at') or 0))
    return out


def _norm(rel_path):
    return str(rel_path).replace('\\', '/').lstrip('/')
