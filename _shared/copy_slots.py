"""copy_slots — the bounded copy-override layer for hand-authored artist pages.

An artist page is `artists/<slug>/<page>/content.md`: hand-written HTML + CSS +
JS where the editable prose is a handful of text nodes. Marking an element
`data-copy="<slot-id>"` (its inner text, plain) or `data-copy-rich="<slot-id>"`
(its inner HTML, restricted to bold/italic/link) makes that content editable
from the artist admin without exposing the layout.

The markup in content.md stays the DEFAULT — the source of truth for "what it
says if nothing overrides it". Overrides live in `artists/<slug>/copy.json`,
shape `{"<page>": {"<slot-id>": "<value>"}}`, and are applied by compile.py at
publish time. An absent or empty copy.json therefore renders the site exactly
as it renders today.

Both consumers parse the same markup — compile.py to substitute, content_admin
to list slots and their defaults for the editor — so the parser lives here once.
Two copies would drift and the editor would start offering slots the compiler
does not fill.

Stdlib only (`re` + `html`): compile.py runs under the bare host python as well
as inside the container, so this module must import with no third-party deps.
"""
import html as _html
import json
import re
from urllib.parse import urlsplit

COPY_FILE = 'copy.json'

# Attribute run that tolerates '>' inside a quoted value.
_ATTRS = r'(?:"[^"]*"|\'[^\']*\'|[^>"\'])*'

_START_TAG_RE = re.compile(r'<([a-zA-Z][\w:-]*)(' + _ATTRS + r')>')
_COPY_ATTR_RE = re.compile(
    r'\bdata-copy(-rich)?\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', re.I)
# <script>/<style> bodies are masked before any scanning: they are not markup,
# and one of them genuinely contains the attribute we look for (the email
# widget emits data-copy on its copy-to-clipboard button).
_OPAQUE_RE = re.compile(r'<(script|style)\b' + _ATTRS + r'>(.*?)</\1\s*>', re.I | re.S)

# Elements that cannot have inner content, so can never carry a slot.
_VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
              'link', 'meta', 'param', 'source', 'track', 'wbr'}

# What a rich slot is allowed to contain, per the convention.
_RICH_TAGS = {'b', 'strong', 'i', 'em', 'a', 'br'}
_ANY_TAG_RE = re.compile(r'<(/?)([a-zA-Z][\w:-]*)(' + _ATTRS + r')/?>')
_OPAQUE_BLOCK_RE = re.compile(r'<(script|style)\b.*?</\1\s*>', re.I | re.S)
_HREF_RE = re.compile(r'\bhref\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', re.I)
_SCHEME_RE = re.compile(r'^([a-z][a-z0-9+.\-]*):', re.I)

# Everything an artist legitimately links to. A schemeless href (relative,
# /absolute-path, #fragment, ?query-only) is always fine; anything carrying a
# scheme has to be one of these. Kept in step with the client-side filter in
# field-editors.js — the editor must never accept a link that publish strips.
_HREF_SCHEMES = {'http', 'https', 'mailto', 'tel'}


def _mask(source):
    """`source` with <script>/<style> bodies blanked out. Same length, so every
    offset found in the mask indexes straight back into the original."""
    out = list(source)
    for m in _OPAQUE_RE.finditer(source):
        for i in range(m.start(2), m.end(2)):
            out[i] = ' '
    return ''.join(out)


def _slot_attr(attrs):
    """(slot-id, rich) for an element's attribute run, or (None, False)."""
    m = _COPY_ATTR_RE.search(attrs)
    if not m:
        return None, False
    slot = (m.group(2) if m.group(2) is not None else m.group(3) or '').strip()
    return (slot or None), bool(m.group(1))


def _close_pos(masked, name, start):
    """(end-tag start, end-tag end) for the element opened before `start`,
    counting nested same-name tags. None if it never closes."""
    pat = re.compile(r'<(/?)' + re.escape(name) + r'(?=[\s/>])', re.I)
    depth = 1
    pos = start
    while True:
        m = pat.search(masked, pos)
        if not m:
            return None
        gt = masked.find('>', m.end())
        if gt == -1:
            return None
        if m.group(1):
            depth -= 1
            if depth == 0:
                return m.start(), gt + 1
        elif not masked[m.end():gt].rstrip().endswith('/'):
            depth += 1
        pos = gt + 1


def find_slots(source):
    """Every copy slot in one page's HTML, in document order.

    Each slot is {'id', 'rich', 'inner_start', 'inner_end', 'inner'} where
    `inner` is the raw source default. Malformed slots (void element,
    self-closing, never closed, no id) are skipped rather than guessed at.
    """
    masked = _mask(source)
    slots = []
    for m in _START_TAG_RE.finditer(masked):
        name, attrs = m.group(1), m.group(2)
        slot, rich = _slot_attr(attrs)
        if not slot:
            continue
        if name.lower() in _VOID_TAGS or attrs.rstrip().endswith('/'):
            continue
        close = _close_pos(masked, name, m.end())
        if close is None:
            continue
        slots.append({'id': slot, 'rich': rich,
                      'inner_start': m.end(), 'inner_end': close[0],
                      'inner': source[m.end():close[0]]})
    return slots


def plain_text(inner):
    """A plain slot's default: the element's text, tags and entities resolved,
    each line trimmed of the source indentation the artist never typed."""
    text = _html.unescape(re.sub(r'<[^>]*>', '', inner))
    lines = [ln.strip() for ln in text.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def apply_overrides(source, values):
    """`source` with each slot's inner content replaced by `values[slot-id]`.

    The element and all of its attributes are preserved byte for byte; only the
    content between its tags changes. Plain slots are escaped, rich slots are
    inserted raw (they are reduced to the allowed subset on write — see
    `sanitize_rich`). A slot with no entry keeps its source default.
    """
    if not values:
        return source
    edits = []
    consumed = -1
    for slot in find_slots(source):
        val = values.get(slot['id'])
        if val is None:
            continue
        # An override wipes everything between the tags, so a slot nested
        # inside one we already replaced no longer exists to be replaced.
        if slot['inner_start'] < consumed:
            continue
        edits.append((slot['inner_start'], slot['inner_end'],
                      str(val) if slot['rich'] else _html.escape(str(val))))
        consumed = slot['inner_end']
    out = source
    for start, end, repl in reversed(edits):
        out = out[:start] + repl + out[end:]
    return out


def _clean_href(attrs):
    """The href from an attribute run, or '' if there isn't a usable one.

    C0 controls are stripped before anything looks at the value: browsers drop
    tab/CR/LF inside a URL, so `java&#9;script:` reaches the parser as
    `javascript:` and would walk straight past a scheme check done on the raw
    string. Spaces are left alone — they are legal in a query or a mailto."""
    m = _HREF_RE.search(attrs)
    if not m:
        return ''
    raw = m.group(1) if m.group(1) is not None else m.group(2)
    href = re.sub(r'[\x00-\x1f\x7f]', '', _html.unescape(raw)).strip()
    scheme = _SCHEME_RE.match(href)
    if scheme and scheme.group(1).lower() not in _HREF_SCHEMES:
        return ''
    return href


def _is_external(href, domain):
    """Whether a link leaves the artist's own site.

    Schemeless hrefs (relative, /path, #frag, ?q=1) and mailto:/tel: never do.
    An http(s) or protocol-relative URL does unless its host is the artist's
    own domain. With no domain to compare against, an absolute URL is assumed
    external — the wrong new tab is a smaller harm than a missing `noopener`.
    """
    if href.lower().startswith(('mailto:', 'tel:')):
        return False
    host = urlsplit(href).hostname if _SCHEME_RE.match(href) or href.startswith('//') else None
    if not host:
        return False
    own = re.sub(r'^www\.', '', (domain or '').strip().lower()
                 .replace('https://', '').replace('http://', '').rstrip('/'))
    return not own or re.sub(r'^www\.', '', host.lower()) != own


def sanitize_rich(value, domain=None):
    """Reduce an editor-supplied rich value to bold/italic/link/break.

    compile.py inserts rich values raw, so this is the gate and it runs on
    write — the client-side restriction is a convenience, not a control.

    `target`/`rel` are DERIVED from the href, never copied from the input. The
    editor (Quill) stamps `target="_blank"` on every link it makes, including
    one to the artist's own contact page, while a hand-authored source default
    may carry a `target` the editor never sees; deriving here is the only place
    that sees the final href, so it is the only place that can be right. An
    anchor left with no usable href is unwrapped to its text rather than
    published dead.
    """
    value = _OPAQUE_BLOCK_RE.sub('', str(value or ''))
    value = re.sub(r'<!--.*?-->', '', value, flags=re.S)
    unwrapped = []          # LIFO: did we drop the <a> whose </a> comes next?

    def _tag(m):
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if name not in _RICH_TAGS:
            return ''
        if name == 'a':
            if closing:
                # Drop the close of an anchor we unwrapped, and any stray one.
                return '' if (not unwrapped or unwrapped.pop()) else '</a>'
            href = _clean_href(attrs)
            unwrapped.append(not href)
            if not href:
                return ''
            out = f'<a href="{_html.escape(href, quote=True)}"'
            if _is_external(href, domain):
                out += ' target="_blank" rel="noopener noreferrer"'
            return out + '>'
        if closing:
            return f'</{name}>'
        return '<br>' if name == 'br' else f'<{name}>'

    return _ANY_TAG_RE.sub(_tag, value)


# ── the store (artists/<slug>/copy.json) ─────────────────────────────────────
def load_store(artist_dir):
    """{page: {slot: value}} for an artist. Missing or malformed reads as empty
    — an artist with no overrides must compile exactly as they do today."""
    try:
        data = json.loads((artist_dir / COPY_FILE).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, dict)}


def save_store(artist_dir, data):
    (artist_dir / COPY_FILE).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
