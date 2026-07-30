"""
Seed data/accounts.db from the existing artists/*/config.json files.

Each artist's current admin_token becomes their initial password, hashed on the
way in. Nobody is locked out and nothing has to be redistributed — the artist's
password is simply what it already was. The accounts DB never holds plaintext,
even though config.json still does.

Idempotent: safe to re-run. Run it inside the container so the relative paths
and the werkzeug import resolve:

    sudo docker exec adze-flask python scripts/backfill_accounts.py --dry-run
    sudo docker exec adze-flask python scripts/backfill_accounts.py
    sudo docker exec adze-flask python scripts/backfill_accounts.py --merge nina serebrenina
    sudo docker exec adze-flask python scripts/backfill_accounts.py --owner gabrielpenman@gmail.com
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '_shared'))

import accounts  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

ARTISTS = Path('artists')

# Not real artists: the template carries literal {{DOMAIN}} placeholders and the
# example is scaffolding. `sandbox` IS kept — it's the live test target.
SKIP = {'_template', 'example-artist'}


def load_configs():
    out = {}
    for d in sorted(ARTISTS.iterdir()):
        if not d.is_dir() or d.name in SKIP or d.name.startswith('.'):
            continue
        p = d / 'config.json'
        if not p.exists():
            continue
        try:
            out[d.name] = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            print(f'  !! {d.name}: UNPARSEABLE config.json ({e}) — SKIPPED. '
                  f'This artist cannot authenticate and will have no account.')
    return out


def plan_identifiers(cfgs):
    """Decide every artist's handles before assigning any.

    A first name claimed by two people is given to NEITHER. First-come-wins is
    arbitrary and hostile: one of the two Jacks would silently log into the
    other's site, or into nothing. Everyone always keeps their slug, so nobody
    is ever left without a working handle.
    """
    first_counts = {}
    for slug, cfg in cfgs.items():
        fn = accounts.first_name_of(cfg.get('name') or slug)
        if fn:
            first_counts.setdefault(fn, []).append(slug)

    contested = {fn: slugs for fn, slugs in first_counts.items() if len(slugs) > 1}

    plan = {}
    for slug, cfg in cfgs.items():
        idents = [(slug, 'slug')]
        fn = accounts.first_name_of(cfg.get('name') or slug)
        if fn and fn not in contested and fn != slug:
            idents.append((fn, 'name'))
        full = accounts.normalise(cfg.get('name'))
        if full and full != fn and full != slug:
            idents.append((full, 'name'))
        dom = accounts.strip_domain(cfg.get('domain') or '')
        if dom and '{{' not in dom:
            idents.append((dom, 'domain'))
        plan[slug] = idents
    return plan, contested


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--merge', nargs=2, metavar=('KEEP', 'ABSORB'),
                    help='merge the ABSORB artist onto the KEEP artist\'s account')
    ap.add_argument('--owner', metavar='EMAIL',
                    help='create/refresh the owner account from $GABRIEL_PASSWORD')
    args = ap.parse_args()

    if args.merge:
        return do_merge(*args.merge, dry=args.dry_run)
    if args.owner:
        return do_owner(args.owner, dry=args.dry_run)

    cfgs = load_configs()
    plan, contested = plan_identifiers(cfgs)

    if contested:
        print('\nContested first names — neither artist gets the bare name:')
        for fn, slugs in sorted(contested.items()):
            print(f'  "{fn}" claimed by {", ".join(slugs)} -> both fall back to slug/domain')

    print(f'\n{len(cfgs)} artists\n')
    created = skipped = 0
    for slug, cfg in sorted(cfgs.items()):
        token = cfg.get('admin_token')
        if not token:
            print(f'  -- {slug}: no admin_token, skipped')
            skipped += 1
            continue

        existing = accounts.resolve(slug)
        handles = ', '.join(i for i, _ in plan[slug])
        if existing:
            print(f'  == {slug}: account #{existing["id"]} exists ({handles})')
            if not args.dry_run:
                accounts.add_site(existing['id'], slug)
                for ident, kind in plan[slug]:
                    accounts.add_identifier(existing['id'], ident, kind)
            skipped += 1
            continue

        print(f'  ++ {slug}: "{cfg.get("name", "")}" -> {handles}')
        created += 1
        if args.dry_run:
            continue

        aid = accounts.create_account(
            display_name=cfg.get('name') or slug,
            password=generate_password_hash(token),
            password_is_hash=True,
            suggested_email=(cfg.get('contact_email') or None),
        )
        accounts.add_site(aid, slug)
        for ident, kind in plan[slug]:
            if not accounts.add_identifier(aid, ident, kind):
                print(f'     !! "{ident}" already claimed — not assigned')

    print(f'\n{"DRY RUN — nothing written" if args.dry_run else "written"}: '
          f'{created} created, {skipped} already present/skipped')

    # contact_email is deliberately NOT adopted as a login handle or a reset
    # target: these are public addresses printed on the artists' own websites.
    # A published login name is bad; a shared inbox that can take over the site
    # is worse. Stored as suggested_email, confirmed by the artist later.
    withmail = [s for s, c in cfgs.items() if c.get('contact_email')]
    if withmail:
        print(f'\n{len(withmail)} artists have a contact_email stored as '
              f'suggested_email (NOT a login handle, NOT a reset target): '
              f'{", ".join(sorted(withmail))}')


def do_merge(keep_slug, absorb_slug, dry=False):
    keep = accounts.resolve(keep_slug)
    absorb = accounts.resolve(absorb_slug)
    if not keep or not absorb:
        print(f'merge: need both accounts to exist ({keep_slug}={bool(keep)}, '
              f'{absorb_slug}={bool(absorb)})')
        return
    if keep['id'] == absorb['id']:
        print('merge: already the same account')
        return
    print(f'merge: #{absorb["id"]} ({absorb_slug}) -> #{keep["id"]} ({keep_slug})')
    print(f'  sites moving: {accounts.sites_for(absorb["id"])}')
    print(f'  {keep_slug} keeps its password; {absorb_slug}\'s is discarded')
    if dry:
        print('  DRY RUN — nothing written')
        return
    db = accounts.get_db()
    db.execute('UPDATE OR IGNORE account_sites SET account_id = ? WHERE account_id = ?',
               (keep['id'], absorb['id']))
    db.execute('UPDATE OR IGNORE account_identifiers SET account_id = ? WHERE account_id = ?',
               (keep['id'], absorb['id']))
    db.execute('DELETE FROM accounts WHERE id = ?', (absorb['id'],))
    db.commit()
    print(f'  done — handles now: {[r["ident"] for r in db.execute(
        "SELECT ident FROM account_identifiers WHERE account_id = ?", (keep["id"],))]}')


def do_owner(email, dry=False):
    pw = os.environ.get('GABRIEL_PASSWORD') or os.environ.get('DEV_ADMIN_TOKEN')
    if not pw:
        print('owner: $GABRIEL_PASSWORD is not set in this container — aborting')
        return
    existing = accounts.resolve(email)
    if existing:
        print(f'owner: account #{existing["id"]} already holds {email}')
        if not dry:
            accounts.set_password(existing['id'], pw)
            print('  password refreshed from $GABRIEL_PASSWORD')
        return
    print(f'owner: create is_owner account for {email} (+ handle "gabriel")')
    if dry:
        print('  DRY RUN — nothing written')
        return
    aid = accounts.create_account(display_name='Gabriel', password=pw,
                                  email=email, is_owner=True)
    accounts.add_identifier(aid, email, 'email')
    accounts.add_identifier(aid, 'gabriel', 'name')
    # No account_sites rows: is_owner short-circuits in session_grants(), so
    # adding an artist never needs a membership backfill.
    print(f'  created account #{aid}')


if __name__ == '__main__':
    main()
