#!/usr/bin/env python3
"""
Migrate data/leads.json into per-artist config.json under a "lead" block.

Non-destructive: dry-run by default. With --apply:
  - existing artist matched by slug → its config.json gains a "lead" block
  - unmatched lead → new artists/<slug>/ scaffold created
  - data/leads.json archived to data/leads.json.pre-merge-bak

Slug matching:
  1. Exact slug match on slugify(client)
  2. Override map (hardcoded for known cases, e.g. "Rose Jones" → "rose")
  3. Otherwise: new artist dir
"""
import argparse
import os
import sys

if os.geteuid() == 0:
    sys.exit(
        "refusing to run as root: this would create root-owned files under "
        "artists/ that the Flask container (uid 1000) cannot write. "
        "re-run as user 'gabriel'."
    )

import json
import re
import secrets
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO / "artists"
LEADS_FILE = REPO / "data" / "leads.json"
ARCHIVE_FILE = REPO / "data" / "leads.json.pre-merge-bak"

# Hand-curated overrides where slugify() of client doesn't match the existing dir.
SLUG_OVERRIDES = {
    "Rose Jones": "rose",
    "Lydia Lott": "lydialott",
    "Mira": "mira",
}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "", name.lower())
    return s or "unnamed"


def lead_to_block(lead: dict) -> dict:
    """Translate a flat lead record into the artist.config.json `lead` block."""
    return {
        "active": lead.get("active", False),
        "contact": lead.get("contact", "") or "",
        "stage": lead.get("stage") or None,
        "fish_size": lead.get("fish_size") or None,
        "instagram": lead.get("instagram", "") or "",
        "work": lead.get("work", "") or "",
        "discount": lead.get("discount", "") or "",
        "notes": lead.get("notes", "") or "",
        "clive_hours": lead.get("clive_hours", 0) or 0,
        "gabe_hours": lead.get("gabe_hours", 0) or 0,
        "contacted": lead.get("contacted", False),
        "original_lead_id": lead.get("id"),
        "created_at": lead.get("created_at"),
        "updated_at": lead.get("updated_at"),
    }


def resolve_slug(client: str, existing: set[str]) -> tuple[str, bool]:
    """Return (slug, is_new)."""
    if client in SLUG_OVERRIDES:
        s = SLUG_OVERRIDES[client]
        return s, s not in existing
    s = slugify(client)
    return s, s not in existing


def scaffold_artist(slug: str, client: str, dry_run: bool) -> None:
    """Create a minimal valid artist directory."""
    art_dir = ARTISTS_DIR / slug
    cfg = {
        "name": client,
        "slug": slug,
        "domain": "",
        "admin_token": secrets.token_urlsafe(8),
        "description": "",
        "contact_email": "",
    }
    if dry_run:
        print(f"  WOULD CREATE {art_dir} with config: name='{client}' slug='{slug}'")
        return
    art_dir.mkdir(parents=True, exist_ok=True)
    (art_dir / "config.json").write_text(json.dumps(cfg, indent=4) + "\n")
    home = art_dir / "home"
    home.mkdir(exist_ok=True)
    (home / "content.md").write_text(f"# {client}\n\nPlaceholder home page.\n")
    page_cfg = {
        "title": client,
        "slug": f"artists/{slug}/home",
        "description": f"{client} — artist",
        "categories": [],
    }
    (home / "config.json").write_text(json.dumps(page_cfg, indent=4) + "\n")


def merge_lead(slug: str, lead: dict, dry_run: bool) -> None:
    cfg_path = ARTISTS_DIR / slug / "config.json"
    block = lead_to_block(lead)
    if dry_run:
        print(f"  WOULD MERGE lead {lead['id'][:8]}… ({lead['client']}) → {cfg_path}")
        print(
            f"    lead block: stage={block['stage']} fish={block['fish_size']} "
            f"active={block['active']} hours(clive/gabe)={block['clive_hours']}/{block['gabe_hours']}"
        )
        return
    cfg = json.loads(cfg_path.read_text())
    if "lead" in cfg:
        print(f"  WARNING: {slug} already has a lead block — overwriting")
    cfg["lead"] = block
    cfg_path.write_text(json.dumps(cfg, indent=4) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write changes")
    args = ap.parse_args()
    dry_run = not args.apply

    if not LEADS_FILE.exists():
        print(f"No {LEADS_FILE} — nothing to migrate.")
        return 0

    leads = json.loads(LEADS_FILE.read_text())
    existing = {p.name for p in ARTISTS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_") and p.name != "AGENTS.md"}

    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"[{mode}] migrating {len(leads)} lead(s)")
    print(f"existing artists: {len(existing)}")
    print()

    seen_slugs: dict[str, str] = {}
    for lead in leads:
        client = lead.get("client", "").strip() or f"unnamed-{lead.get('id', '?')[:8]}"
        slug, is_new = resolve_slug(client, existing)
        if slug in seen_slugs:
            print(f"  COLLISION: '{client}' and '{seen_slugs[slug]}' both → {slug}; appending hash")
            slug = f"{slug}{lead['id'][:4]}"
            is_new = slug not in existing
        seen_slugs[slug] = client
        action = "scaffold + merge" if is_new else "merge into existing"
        print(f"- {client}  →  artists/{slug}/  [{action}]")
        if is_new:
            scaffold_artist(slug, client, dry_run)
        merge_lead(slug, lead, dry_run)
        if not dry_run:
            existing.add(slug)
        print()

    if dry_run:
        print(f"[DRY-RUN complete] re-run with --apply to write changes.")
        print(f"Note: data/leads.json would be archived to {ARCHIVE_FILE.name}.")
    else:
        shutil.move(str(LEADS_FILE), str(ARCHIVE_FILE))
        print(f"Archived original to {ARCHIVE_FILE}.")
        print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
