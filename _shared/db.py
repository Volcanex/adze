"""
Per-artist SQLite database helper.

Each artist gets one file: artists/{slug}/data.db
Tables: pageviews, sessions

All other data (subscribers, submissions, config, pages) stays in JSON —
only the high-frequency append-heavy time-series data lives here.
"""

import sqlite3
import threading
from pathlib import Path

# Per-artist connection cache — one persistent connection per slug, thread-safe
_connections = {}
_connections_lock = threading.Lock()


def get_db(artist_slug: str) -> sqlite3.Connection:
    """
    Return a thread-local SQLite connection for the given artist.
    Creates the database and tables on first access.
    """
    db_path = Path(f'artists/{artist_slug}/data.db')
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with _connections_lock:
        if artist_slug not in _connections:
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # WAL mode: readers don't block writers, great for concurrent web requests
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            _init_schema(conn)
            _connections[artist_slug] = conn
        return _connections[artist_slug]


def _init_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS pageviews (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            path    TEXT    NOT NULL,
            ts      INTEGER NOT NULL,
            ref     TEXT    DEFAULT '',
            country TEXT    DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_pv_ts      ON pageviews(ts);
        CREATE INDEX IF NOT EXISTS idx_pv_path    ON pageviews(path, ts);
        CREATE INDEX IF NOT EXISTS idx_pv_country ON pageviews(country, ts);

        CREATE TABLE IF NOT EXISTS sessions (
            sid     TEXT    PRIMARY KEY,
            dur     INTEGER DEFAULT 0,
            pc      INTEGER DEFAULT 1,
            ts      INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sess_ts ON sessions(ts);
    """)
    conn.commit()


# ── Pageviews ──────────────────────────────────────────────────────────────

def insert_pageview(artist_slug: str, path: str, ts: int, ref: str = '', country: str = ''):
    conn = get_db(artist_slug)
    with _connections_lock:
        conn.execute(
            'INSERT INTO pageviews (path, ts, ref, country) VALUES (?, ?, ?, ?)',
            (path, ts, ref, country)
        )
        conn.commit()


def query_analytics(artist_slug: str, month_start: int, prev_month_start: int,
                    today_start: int, week_start: int):
    """
    Return all analytics aggregates in one pass.
    Returns a dict matching the old JSON-based structure.
    """
    from datetime import datetime, timedelta

    conn = get_db(artist_slug)

    # Counts
    row = conn.execute("""
        SELECT
            COUNT(*) FILTER (WHERE ts >= ?) AS today,
            COUNT(*) FILTER (WHERE ts >= ?) AS week,
            COUNT(*) FILTER (WHERE ts >= ?) AS month,
            COUNT(*) FILTER (WHERE ts >= ? AND ts < ?) AS prev_month
        FROM pageviews
    """, (today_start, week_start, month_start, prev_month_start, month_start)).fetchone()

    today_count    = row['today']
    week_count     = row['week']
    month_count    = row['month']
    prev_month_count = row['prev_month']

    # Top pages (last 30 days)
    top_pages = [
        {'path': r['path'], 'views': r['cnt']}
        for r in conn.execute(
            "SELECT path, COUNT(*) AS cnt FROM pageviews WHERE ts >= ? GROUP BY path ORDER BY cnt DESC LIMIT 20",
            (month_start,)
        )
    ]

    # Sources (last 30 days)
    sources = [
        {'source': r['ref'], 'views': r['cnt']}
        for r in conn.execute(
            "SELECT ref, COUNT(*) AS cnt FROM pageviews WHERE ts >= ? AND ref != '' GROUP BY ref ORDER BY cnt DESC LIMIT 20",
            (month_start,)
        )
    ]

    # Countries (last 30 days)
    countries = [
        {'country': r['country'], 'views': r['cnt']}
        for r in conn.execute(
            "SELECT country, COUNT(*) AS cnt FROM pageviews WHERE ts >= ? AND country != '' GROUP BY country ORDER BY cnt DESC LIMIT 20",
            (month_start,)
        )
    ]

    # Daily counts — last 30 days, one row per day
    daily_rows = conn.execute(
        "SELECT date(ts, 'unixepoch') AS day, COUNT(*) AS cnt FROM pageviews WHERE ts >= ? GROUP BY day",
        (month_start,)
    ).fetchall()
    daily_map = {r['day']: r['cnt'] for r in daily_rows}
    daily = []
    for i in range(29, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        daily.append({'date': d, 'views': daily_map.get(d, 0)})

    # Hourly distribution (last 30 days)
    hourly_rows = conn.execute(
        "SELECT strftime('%H', ts, 'unixepoch') AS hr, COUNT(*) AS cnt FROM pageviews WHERE ts >= ? GROUP BY hr",
        (month_start,)
    ).fetchall()
    hourly_counts = [0] * 24
    for r in hourly_rows:
        hourly_counts[int(r['hr'])] = r['cnt']

    return {
        'today_count': today_count,
        'week_count': week_count,
        'month_count': month_count,
        'prev_month_count': prev_month_count,
        'top_pages': top_pages,
        'sources': sources,
        'countries': countries,
        'daily': daily,
        'hourly_counts': hourly_counts,
    }


# ── Sessions ───────────────────────────────────────────────────────────────

def upsert_session(artist_slug: str, sid: str, dur: int, pc: int, ts: int):
    """Insert or update a session, keeping max dur and pc seen."""
    conn = get_db(artist_slug)
    with _connections_lock:
        conn.execute("""
            INSERT INTO sessions (sid, dur, pc, ts) VALUES (?, ?, ?, ?)
            ON CONFLICT(sid) DO UPDATE SET
                dur = MAX(dur, excluded.dur),
                pc  = MAX(pc,  excluded.pc),
                ts  = excluded.ts
        """, (sid, dur, pc, ts))
        # Prune sessions older than 60 days (cheap — runs on every write)
        cutoff = ts - 60 * 86400
        conn.execute('DELETE FROM sessions WHERE ts < ?', (cutoff,))
        conn.commit()


def query_sessions(artist_slug: str, since_ts: int):
    """Return bounce rate and avg duration for sessions since since_ts."""
    conn = get_db(artist_slug)
    rows = conn.execute(
        'SELECT dur, pc FROM sessions WHERE ts >= ?', (since_ts,)
    ).fetchall()

    total = len(rows)
    if total == 0:
        return {'bounce_rate': 0, 'avg_duration': 0, 'total_sessions': 0}

    bounces   = sum(1 for r in rows if r['pc'] <= 1)
    durations = [r['dur'] for r in rows if r['dur'] > 0]
    return {
        'bounce_rate':    round(bounces / total * 100, 1),
        'avg_duration':   round(sum(durations) / len(durations)) if durations else 0,
        'total_sessions': total,
    }


# ── Migration helper ────────────────────────────────────────────────────────

def migrate_json_to_sqlite(artist_slug: str):
    """
    One-time import of existing analytics.json and sessions.json into SQLite.
    Safe to call multiple times — uses INSERT OR IGNORE for pageviews (no unique
    key so it will re-insert; call only once or wipe the DB first).
    Deletes the JSON files afterwards so they don't accumulate.
    """
    import json
    from pathlib import Path

    artist_path = Path(f'artists/{artist_slug}')
    conn = get_db(artist_slug)

    # Pageviews
    analytics_file = artist_path / 'analytics.json'
    if analytics_file.exists():
        try:
            entries = json.loads(analytics_file.read_text())
            with _connections_lock:
                conn.executemany(
                    'INSERT INTO pageviews (path, ts, ref, country) VALUES (?, ?, ?, ?)',
                    [(e.get('path',''), e.get('ts',0), e.get('ref',''), e.get('country',''))
                     for e in entries if isinstance(e, dict)]
                )
                conn.commit()
            analytics_file.rename(analytics_file.with_suffix('.json.bak'))
        except Exception as exc:
            print(f'[db] Migration warning (pageviews/{artist_slug}): {exc}')

    # Sessions
    sessions_file = artist_path / 'sessions.json'
    if sessions_file.exists():
        try:
            sessions = json.loads(sessions_file.read_text())
            with _connections_lock:
                conn.executemany(
                    'INSERT OR REPLACE INTO sessions (sid, dur, pc, ts) VALUES (?, ?, ?, ?)',
                    [(sid, v.get('dur',0), v.get('pc',1), v.get('ts',0))
                     for sid, v in sessions.items() if isinstance(v, dict)]
                )
                conn.commit()
            sessions_file.rename(sessions_file.with_suffix('.json.bak'))
        except Exception as exc:
            print(f'[db] Migration warning (sessions/{artist_slug}): {exc}')
