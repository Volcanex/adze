"""Per-artist lead / CRM store, kept OUT of the artist-editable tree.

Leads used to live inside each artist's `config.json` under a `lead` block
(see the retired `scripts/merge-leads-into-artists.py`). That put our internal
CRM — fish_size, hours, discount, private notes — inside the very directory the
Auto-Code and Terminal agents are rooted at, so their filesystem tools could
read it back verbatim. Leads now live in `data/leads/<slug>.json` instead:
outside every artist directory, so no site-editing agent can reach them.

`data/` is gitignored, so lead data also stops being committed to the repo.
One-time move: `scripts/extract-leads-from-config.py`.
"""

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
LEADS_DIR = _ROOT / 'data' / 'leads'


def _path(slug: str) -> Path:
    return LEADS_DIR / f'{slug}.json'


def read_lead(slug: str):
    """Return this artist's lead block, or None if they have no lead."""
    p = _path(slug)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


def write_lead(slug: str, lead: dict) -> dict:
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    _path(slug).write_text(
        json.dumps(lead, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    return lead


def delete_lead(slug: str) -> bool:
    try:
        _path(slug).unlink()
        return True
    except FileNotFoundError:
        return False


def all_leads() -> dict:
    """Map slug -> lead block for every artist that has one."""
    out = {}
    if not LEADS_DIR.exists():
        return out
    for p in sorted(LEADS_DIR.glob('*.json')):
        try:
            out[p.stem] = json.loads(p.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            pass
    return out
