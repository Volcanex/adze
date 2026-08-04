"""
Central account store — data/accounts.db

The one place a login is decided. Distinct from db.py, which is per-artist
time-series (artists/<slug>/data.db); this is a single studio-wide file, and
it is the only database in Adze that is not scoped to one artist.

Why a real store at all: before this, the credential WAS the cookie value —
adze_session held "<slug>:<plaintext admin_token>" and every consumer
re-verified it as a live password. Hashing passwords makes that impossible, so
sessions have to become opaque ids that resolve to something. That something
is here.

The session id is prefixed `as1_` on purpose. is_admin_token() and
verify_artist_token() run on every API request, and the prefix lets them fall
through to the legacy path on a string comparison with no database hit. It also
makes a session id structurally impossible to confuse with an admin_token.

Identifiers (name, email, slug, domain) share ONE flat namespace in
account_identifiers. That is what makes "log in with your first name OR your
email" a single indexed lookup with no precedence rules, makes adding an email
later a plain INSERT, and makes it impossible for a name to shadow an email.
"""

import os
import re
import sqlite3
import secrets
import hashlib
import threading
import time
from pathlib import Path

from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = Path('data/accounts.db')

SESSION_PREFIX = 'as1_'
SESSION_TTL = 30 * 24 * 3600        # 30 days, rolling
RESET_TTL = 60 * 60                 # 1 hour, single use
HANDOFF_TTL = 60                    # 60 s, single use — intake -> own-domain hop
_SESSION_CACHE_TTL = 60             # seconds; sessions are read on every request
_LAST_SEEN_INTERVAL = 3600          # don't write last_seen_at more than hourly

_conn = None
_lock = threading.Lock()
_session_cache = {}                 # sid -> (record|None, fetched_at)


def get_db():
    global _conn
    with _lock:
        if _conn is None:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
            c.row_factory = sqlite3.Row
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('PRAGMA synchronous=NORMAL')
            c.execute('PRAGMA foreign_keys=ON')
            _init_schema(c)
            _conn = c
        return _conn


def _init_schema(conn):
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS accounts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name    TEXT    NOT NULL DEFAULT '',
            email           TEXT,
            email_verified  INTEGER NOT NULL DEFAULT 0,
            suggested_email TEXT,
            password_hash   TEXT    NOT NULL,
            is_owner        INTEGER NOT NULL DEFAULT 0,
            disabled        INTEGER NOT NULL DEFAULT 0,
            created_at      INTEGER NOT NULL,
            updated_at      INTEGER NOT NULL,
            last_login_at   INTEGER,
            last_login_ip   TEXT
        );

        -- One flat namespace for every way you can type your name. A name can
        -- never shadow an email because they share this primary key.
        CREATE TABLE IF NOT EXISTS account_identifiers (
            ident      TEXT    PRIMARY KEY,
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            kind       TEXT    NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ident_acct ON account_identifiers(account_id);

        CREATE TABLE IF NOT EXISTS account_sites (
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            slug       TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'owner',
            created_at INTEGER NOT NULL,
            PRIMARY KEY (account_id, slug)
        );
        CREATE INDEX IF NOT EXISTS idx_sites_slug ON account_sites(slug);

        CREATE TABLE IF NOT EXISTS auth_sessions (
            sid             TEXT    PRIMARY KEY,
            account_id      INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            slug            TEXT    NOT NULL,
            impersonated_by INTEGER,
            created_at      INTEGER NOT NULL,
            last_seen_at    INTEGER NOT NULL,
            expires_at      INTEGER NOT NULL,
            ip              TEXT,
            ua              TEXT,
            revoked         INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_sess_acct ON auth_sessions(account_id);

        -- Only the sha256 of the emailed token is stored; the raw value exists
        -- in exactly one place, the artist's inbox.
        CREATE TABLE IF NOT EXISTS password_resets (
            token_hash TEXT PRIMARY KEY,
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            used_at    INTEGER,
            ip         TEXT
        );

        -- One-time nonce that carries an intake-portal login across to the
        -- artist's own domain, where /enter swaps it for a session cookie. Same
        -- hash-at-rest shape as password_resets; slug-bound so a nonce minted
        -- for one artist can never authenticate another.
        CREATE TABLE IF NOT EXISTS handoff_nonces (
            token_hash TEXT PRIMARY KEY,
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            slug       TEXT    NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            used_at    INTEGER
        );
    ''')
    conn.commit()


# ── identifiers ───────────────────────────────────────────────────────────────

def normalise(s):
    """Identifiers are stored already-normalised so lookup is one indexed
    SELECT rather than a LOWER() table scan."""
    if not s:
        return ''
    s = str(s).strip().strip('"\'').lower()
    return re.sub(r'\s+', ' ', s)


def first_name_of(full_name):
    """'Jack Dennison-Thompson' -> 'jack'. Non-alphanumerics stripped so
    'Jean-Luc' and 'O'Brien' land somewhere typeable."""
    first = normalise(full_name).split(' ')[0] if full_name else ''
    return re.sub(r'[^a-z0-9]', '', first)


def strip_domain(d):
    d = normalise(d)
    d = re.sub(r'^https?://', '', d)
    d = re.sub(r'^www\.', '', d)
    return d.rstrip('/').split('/')[0]


def add_identifier(account_id, ident, kind):
    """Claim an identifier. Returns False if another account already holds it —
    never steals, so a collision is always visible to the caller."""
    ident = normalise(ident)
    if not ident:
        return False
    db = get_db()
    row = db.execute('SELECT account_id FROM account_identifiers WHERE ident = ?',
                     (ident,)).fetchone()
    if row:
        return row['account_id'] == account_id
    db.execute('INSERT INTO account_identifiers (ident, account_id, kind, created_at) '
               'VALUES (?, ?, ?, ?)', (ident, account_id, kind, int(time.time())))
    db.commit()
    return True


def resolve(identifier):
    """identifier (name | email | slug | domain) -> account row, or None."""
    ident = normalise(identifier)
    if not ident:
        return None
    db = get_db()
    row = db.execute(
        'SELECT a.* FROM account_identifiers i JOIN accounts a ON a.id = i.account_id '
        'WHERE i.ident = ? AND a.disabled = 0', (ident,)).fetchone()
    return row


# ── accounts ──────────────────────────────────────────────────────────────────

def create_account(display_name, password, email=None, suggested_email=None,
                   is_owner=False, password_is_hash=False):
    now = int(time.time())
    db = get_db()
    cur = db.execute(
        'INSERT INTO accounts (display_name, email, email_verified, suggested_email, '
        'password_hash, is_owner, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (display_name or '', email, 1 if email else 0, suggested_email,
         password if password_is_hash else generate_password_hash(password),
         1 if is_owner else 0, now, now))
    db.commit()
    return cur.lastrowid


def get_account(account_id):
    return get_db().execute('SELECT * FROM accounts WHERE id = ?', (account_id,)).fetchone()


def verify_password(account, password):
    if not account or account['disabled']:
        return False
    return check_password_hash(account['password_hash'], password or '')


def set_password(account_id, new_password):
    db = get_db()
    db.execute('UPDATE accounts SET password_hash = ?, updated_at = ? WHERE id = ?',
               (generate_password_hash(new_password), int(time.time()), account_id))
    db.commit()


def add_site(account_id, slug, role='owner'):
    db = get_db()
    db.execute('INSERT OR IGNORE INTO account_sites (account_id, slug, role, created_at) '
               'VALUES (?, ?, ?, ?)', (account_id, slug, role, int(time.time())))
    db.commit()


def sites_for(account_id):
    return [r['slug'] for r in get_db().execute(
        'SELECT slug FROM account_sites WHERE account_id = ? ORDER BY slug', (account_id,))]


def account_for_slug(slug):
    return get_db().execute(
        'SELECT a.* FROM account_sites s JOIN accounts a ON a.id = s.account_id '
        'WHERE s.slug = ? AND a.disabled = 0 ORDER BY s.created_at LIMIT 1',
        (slug,)).fetchone()


def record_login(account_id, ip):
    db = get_db()
    db.execute('UPDATE accounts SET last_login_at = ?, last_login_ip = ? WHERE id = ?',
               (int(time.time()), ip or '', account_id))
    db.commit()


# ── sessions ──────────────────────────────────────────────────────────────────

def create_session(account_id, slug, ip=None, ua=None, impersonated_by=None):
    sid = SESSION_PREFIX + secrets.token_urlsafe(32)
    now = int(time.time())
    db = get_db()
    db.execute(
        'INSERT INTO auth_sessions (sid, account_id, slug, impersonated_by, created_at, '
        'last_seen_at, expires_at, ip, ua) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (sid, account_id, slug, impersonated_by, now, now, now + SESSION_TTL,
         (ip or '')[:64], (ua or '')[:300]))
    db.commit()
    return sid


def lookup_session(sid):
    """Cached for 60s — this runs on every authenticated request."""
    if not sid or not sid.startswith(SESSION_PREFIX):
        return None
    hit = _session_cache.get(sid)
    now = time.time()
    if hit and now - hit[1] < _SESSION_CACHE_TTL:
        return hit[0]
    row = get_db().execute(
        'SELECT s.*, a.is_owner, a.display_name, a.disabled FROM auth_sessions s '
        'JOIN accounts a ON a.id = s.account_id WHERE s.sid = ?', (sid,)).fetchone()
    rec = None
    if row and not row['revoked'] and not row['disabled'] and row['expires_at'] > now:
        rec = dict(row)
        if now - row['last_seen_at'] > _LAST_SEEN_INTERVAL:
            db = get_db()
            db.execute('UPDATE auth_sessions SET last_seen_at = ? WHERE sid = ?',
                       (int(now), sid))
            db.commit()
    _session_cache[sid] = (rec, now)
    return rec


def session_grants(sid, slug):
    """Does this session authorise acting as `slug`?"""
    rec = lookup_session(sid)
    if not rec:
        return False
    if rec['is_owner']:
        return True                       # the owner can act as any artist
    if rec['slug'] == slug:
        return True
    return any(s == slug for s in sites_for(rec['account_id']))


def session_is_owner(sid):
    rec = lookup_session(sid)
    return bool(rec and rec['is_owner'])


def session_identity(sid):
    """Shape matches auth.ADMIN_IDENTITIES entries so get_identity_by_token can
    return this straight through."""
    rec = lookup_session(sid)
    if not rec or not rec['is_owner']:
        return None
    return {
        'username': (rec['display_name'] or 'owner').lower(),
        'password': '',                   # never round-trips a credential
        'name': rec['display_name'] or 'Owner',
        'workspaces': ['personal', 'lastplace'],
        'super': True,
    }


def revoke_session(sid):
    db = get_db()
    db.execute('UPDATE auth_sessions SET revoked = 1 WHERE sid = ?', (sid,))
    db.commit()
    _session_cache.pop(sid, None)


def revoke_all_for_account(account_id, except_sid=None):
    db = get_db()
    db.execute('UPDATE auth_sessions SET revoked = 1 WHERE account_id = ? AND sid != ?',
               (account_id, except_sid or ''))
    db.commit()
    _session_cache.clear()


# ── password reset ────────────────────────────────────────────────────────────

def _hash_token(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def create_reset(account_id, ip=None):
    raw = secrets.token_urlsafe(32)
    now = int(time.time())
    db = get_db()
    db.execute('INSERT INTO password_resets (token_hash, account_id, created_at, '
               'expires_at, ip) VALUES (?, ?, ?, ?, ?)',
               (_hash_token(raw), account_id, now, now + RESET_TTL, (ip or '')[:64]))
    db.commit()
    return raw


def consume_reset(raw_token):
    """Single use. Returns account_id, or None if unknown/expired/spent."""
    if not raw_token:
        return None
    db = get_db()
    row = db.execute('SELECT * FROM password_resets WHERE token_hash = ?',
                     (_hash_token(raw_token),)).fetchone()
    if not row or row['used_at'] or row['expires_at'] < time.time():
        return None
    db.execute('UPDATE password_resets SET used_at = ? WHERE token_hash = ?',
               (int(time.time()), row['token_hash']))
    db.commit()
    return row['account_id']


# ── intake -> own-domain handoff ──────────────────────────────────────────────

def create_handoff(account_id, slug):
    """One-time, 60-second token that carries an intake-portal login across to
    the artist's own domain, where /enter swaps it for a first-party session
    cookie. Only the hash is stored; the raw value lives in the redirect URL for
    exactly one hop — like a password reset but far shorter-lived and weaker (it
    grants a session, not a password change)."""
    raw = secrets.token_urlsafe(32)
    now = int(time.time())
    db = get_db()
    db.execute('INSERT INTO handoff_nonces (token_hash, account_id, slug, '
               'created_at, expires_at) VALUES (?, ?, ?, ?, ?)',
               (_hash_token(raw), account_id, slug, now, now + HANDOFF_TTL))
    db.commit()
    return raw


def consume_handoff(raw_token, slug):
    """Single use. Returns account_id only if the nonce is live AND was minted
    for `slug` — so a nonce for one artist can't authenticate another. Marks it
    spent so a leaked URL can't be replayed."""
    if not raw_token:
        return None
    db = get_db()
    row = db.execute('SELECT * FROM handoff_nonces WHERE token_hash = ?',
                     (_hash_token(raw_token),)).fetchone()
    if not row or row['used_at'] or row['expires_at'] < time.time() \
            or row['slug'] != slug:
        return None
    db.execute('UPDATE handoff_nonces SET used_at = ? WHERE token_hash = ?',
               (int(time.time()), row['token_hash']))
    db.commit()
    return row['account_id']
