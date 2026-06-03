"""Shared asset storage primitives — the common core behind both the admin
dashboard (`/api/adze/*`) and the public intake portal
(`/api/adze/intake/<slug>/<token>/*`).

Both surfaces are "different sides of the same system": they write into the
same `artists/<slug>/assets/` tree, mirror to `output/artists/<slug>/assets/`
so nginx can serve files live, and record metadata via `asset_meta`. This
module holds the logic they share so folder/zip support behaves identically on
both sides:

- `safe_rel()`     — sanitise a client-supplied relative path (Zip-Slip guard).
- `store_fileobj()`— save one upload at a chosen relative path + mirror + meta.
- `extract_zip()`  — unpack a zip preserving its folder tree, with an
                     extension policy and file-count / byte caps.

Paths are POSIX (forward slashes), relative to the artist's `assets/` dir.
This module deliberately does NOT import `admin_api` (that would be circular);
callers pass in their own extension policy.
"""
import io
import shutil
import logging
import tempfile
import time as _time
import zipfile
from pathlib import Path

from werkzeug.utils import secure_filename

import asset_meta

_THUMB_IMAGE_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'tif', 'avif'}
_THUMB_SIZE = 64  # px — must match compile.py expectation


def _generate_thumb(dest_path, assets_root):
    """Generate a 24×24 WebP thumbnail sidecar for an image asset.
    Stored at assets_root/.thumbs/<same-rel>.webp. Best-effort — never raises."""
    ext = dest_path.suffix.lower().lstrip('.')
    if ext not in _THUMB_IMAGE_EXTS:
        return
    try:
        from PIL import Image
        import io as _bio
        thumb_rel  = dest_path.relative_to(assets_root)
        thumb_path = assets_root / '.thumbs' / thumb_rel.with_suffix('.webp')
        thumb_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(dest_path) as img:
            img = img.convert('RGB')
            img.thumbnail((_THUMB_SIZE, _THUMB_SIZE), Image.LANCZOS)
            buf = _bio.BytesIO()
            img.save(buf, 'WEBP', quality=70, method=6)
            thumb_path.write_bytes(buf.getvalue())
    except Exception as e:
        logging.debug('thumb generation skipped for %s: %s', dest_path.name, e)


def assets_dir(slug):
    return Path('artists') / slug / 'assets'


def output_dir(slug):
    return Path('output/artists') / slug / 'assets'


def safe_rel(rel):
    """Sanitise a client-supplied relative path into a safe POSIX rel path.

    Splits on '/', runs each segment through `secure_filename` (which strips
    path separators, '..', and unsafe chars), and drops '.'/empty segments.
    Returns the cleaned 'a/b/c.ext' string, or None if nothing usable remains
    or the path tried to escape (e.g. '../', absolute, all-unicode names).
    """
    if not rel:
        return None
    rel = str(rel).replace('\\', '/').strip().lstrip('/')
    parts = []
    for seg in rel.split('/'):
        seg = seg.strip()
        if not seg or seg == '.':
            continue
        if seg == '..':
            return None
        safe = secure_filename(seg)
        if not safe:
            return None
        parts.append(safe)
    return '/'.join(parts) or None


def _mirror_to_output(slug, rel):
    """Copy a stored asset into the output/ mirror so nginx serves it live.
    Best-effort: the output dir may be host-owned / unwritable from the
    container, in which case the canonical copy under artists/ still stands."""
    try:
        src = assets_dir(slug) / rel
        out = output_dir(slug) / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(out))
    except (OSError, PermissionError) as err:
        logging.warning('asset output mirror failed for %s: %s', rel, err)


def store_fileobj(slug, rel, fileobj, *, uploaded_by, uploaded_at=None,
                  labels=None):
    """Save one uploaded file at `rel` under the artist's assets dir,
    preserving any folder structure in `rel`, mirror it to output/, and record
    metadata. `fileobj` is a Werkzeug FileStorage (has `.save`). Returns the
    cleaned rel path, or None if `rel` sanitised to nothing.
    """
    rel = safe_rel(rel)
    if not rel:
        return None
    dest = assets_dir(slug) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    fileobj.save(str(dest))
    _generate_thumb(dest, assets_dir(slug))
    _mirror_to_output(slug, rel)
    asset_meta.update_for(slug, rel,
                          uploaded_by=uploaded_by,
                          uploaded_at=uploaded_at or int(_time.time()),
                          labels=list(labels) if labels else None)
    return rel


def _is_junk_member(name):
    """Skip archive cruft: macOS resource forks and dotfiles in any segment."""
    if '__MACOSX' in name:
        return True
    return any(seg.startswith('.') for seg in name.replace('\\', '/').split('/') if seg)


def extract_zip(slug, zip_source, *, dest_prefix='', is_allowed=None,
                uploaded_by, uploaded_at=None, labels=None,
                max_files=2000, max_total_bytes=None):
    """Unpack a zip into the artist's assets dir, preserving its folder tree.

    Args:
        zip_source:   a filesystem path/str, or a seekable file-like object.
        dest_prefix:  rel prefix every member lands under (e.g. 'intake').
        is_allowed:   fn(ext_without_dot) -> bool. Members failing it are
                      skipped (the container being a .zip says nothing about
                      what's safe inside it). Default: allow everything.
        max_files:    stop after this many members (guards zip bombs / runaway).
        max_total_bytes: stop once cumulative uncompressed bytes exceed this.

    Returns {'stored': [rel...], 'skipped': [name...], 'truncated': bool,
             'bytes': int}.
    """
    if is_allowed is None:
        is_allowed = lambda ext: True
    stored, skipped = [], []
    truncated = False
    total = 0
    uploaded_at = uploaded_at or int(_time.time())
    labels = list(labels) if labels else None

    # A malformed / non-zip upload is a client error, not a server crash.
    try:
        zf = zipfile.ZipFile(zip_source)
    except (zipfile.BadZipFile, OSError) as err:
        return {'stored': [], 'skipped': [], 'truncated': False,
                'bytes': 0, 'error': f'Not a readable zip: {err}'}

    with zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename
            if _is_junk_member(name):
                skipped.append(name)
                continue
            combined = f'{dest_prefix}/{name}' if dest_prefix else name
            rel = safe_rel(combined)
            if not rel:
                skipped.append(name)
                continue
            ext = rel.rsplit('.', 1)[-1].lower() if '.' in rel else ''
            if not is_allowed(ext):
                skipped.append(name)
                continue
            if len(stored) >= max_files:
                truncated = True
                break
            if max_total_bytes is not None and total + info.file_size > max_total_bytes:
                truncated = True
                break
            # One unreadable member (encrypted, unsupported compression such as
            # deflate64, bad CRC, …) must not sink the whole archive — skip it.
            try:
                data = zf.read(info)
                dest = assets_dir(slug) / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            except (RuntimeError, NotImplementedError, zipfile.BadZipFile, OSError) as err:
                logging.warning('zip member %r skipped: %s', name, err)
                skipped.append(name)
                continue
            total += len(data)
            _generate_thumb(dest, assets_dir(slug))
            _mirror_to_output(slug, rel)
            asset_meta.update_for(slug, rel,
                                  uploaded_by=uploaded_by,
                                  uploaded_at=uploaded_at,
                                  labels=labels)
            stored.append(rel)

    return {'stored': stored, 'skipped': skipped,
            'truncated': truncated, 'bytes': total}


def save_temp_upload(fileobj):
    """Spool a Werkzeug FileStorage to a NamedTemporaryFile and return its path.
    Useful for zips: gives `extract_zip` a stable seekable source regardless of
    how Werkzeug buffered the multipart part. Caller must unlink the path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    fileobj.save(tmp.name)
    tmp.close()
    return tmp.name
