#!/usr/bin/env python3
"""
Move the `lead` block OUT of each artist's config.json into data/leads/<slug>.json.

The inverse of the retired scripts/merge-leads-into-artists.py. Leads are our
internal CRM; keeping them in config.json exposed them to the Auto-Code /
Terminal agents, whose file tools are rooted at the artist directory. This
relocates them outside every artist dir.

Dry-run by default; pass --apply to write. Idempotent: an artist whose
config.json already has no `lead` block is skipped.

Run as the Flask container's user (uid 1000), NOT root, so the rewritten
config.json stays writable by the app:
    docker exec adze-flask python /app/scripts/extract-leads-from-config.py --apply
"""
import argparse
import json
import os
import sys
from pathlib import Path

if os.geteuid() == 0:
    sys.exit(
        "refusing to run as root: rewriting config.json as root makes it "
        "unwritable by the Flask container (uid 1000). Run inside the "
        "container: docker exec adze-flask python "
        "/app/scripts/extract-leads-from-config.py --apply"
    )

REPO = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO / "artists"
LEADS_DIR = REPO / "data" / "leads"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    if not ARTISTS_DIR.is_dir():
        sys.exit(f"no artists dir at {ARTISTS_DIR}")

    moved = skipped = 0
    for cfg_path in sorted(ARTISTS_DIR.glob("*/config.json")):
        slug = cfg_path.parent.name
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"  ! {slug}: unreadable config.json ({exc})")
            continue
        if "lead" not in cfg:
            skipped += 1
            continue

        lead = cfg["lead"]
        dest = LEADS_DIR / f"{slug}.json"
        print(f"  → {slug}: lead → data/leads/{slug}.json")
        if args.apply:
            LEADS_DIR.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(lead, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            del cfg["lead"]
            cfg_path.write_text(json.dumps(cfg, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        moved += 1

    verb = "moved" if args.apply else "would move"
    print(f"\n{verb} {moved} lead block(s); {skipped} artist(s) had none.")
    if not args.apply:
        print("dry-run only — re-run with --apply to write.")


if __name__ == "__main__":
    main()
