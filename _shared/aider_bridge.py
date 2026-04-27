"""
Claude Code over WebSocket — pty bridge.

Each connected dashboard tab gets its own `claude` (Claude Code CLI)
subprocess running inside a pty, streamed bidirectionally via Socket.IO.
The frontend renders the stream via xterm.js; UI buttons (Asset / Pointer
/ +) inject text into the pty.

Why Claude Code, not aider:
  Aider's UX is built around explicit /add. Artists can't be doing that.
  Claude Code's Read tool reads files autonomously when needed — same
  experience the user already has in the terminal locally. The only
  difference here is it's running in the dashboard pane instead of a
  terminal window, scoped to the artist's directory.

The module name is still `aider_bridge` for git history continuity; rename
to `claude_terminal.py` is a follow-up that's not worth the import churn
right now.
"""

from __future__ import annotations

import os
import pty
import fcntl
import struct
import signal
import termios
import subprocess
import threading
import logging
from pathlib import Path
from flask import request


def _verify(artist_slug: str, token: str) -> bool:
    from auth import verify_artist_token
    return verify_artist_token(artist_slug, token)


_log = logging.getLogger('adze.claude')


# Where the platform's vibe-coder docs live — fed to Claude as the
# system prompt so it understands Adze conventions.
_DOCS_DIR = Path(__file__).parent / 'docs'


# Allow-list copied from the legacy claude-stream subprocess code at
# admin_api.py — sandboxes Claude's Bash to safe operations only. No
# sudo, systemctl, ssh, mount, kill, etc. Combined with
# --permission-mode acceptEdits, file edits inside cwd auto-confirm
# but operations escaping cwd are blocked.
ALLOWED_TOOLS = [
    'Read', 'Write', 'Edit', 'Glob', 'Grep',
    # File ops
    'Bash(ls:*)', 'Bash(mkdir:*)', 'Bash(cp:*)', 'Bash(mv:*)', 'Bash(rm:*)',
    'Bash(touch:*)', 'Bash(chmod:*)', 'Bash(chown:*)', 'Bash(ln:*)',
    'Bash(basename:*)', 'Bash(dirname:*)', 'Bash(realpath:*)', 'Bash(readlink:*)',
    'Bash(find:*)', 'Bash(tree:*)', 'Bash(pwd:*)', 'Bash(cd:*)',
    'Bash(stat:*)', 'Bash(file:*)', 'Bash(du:*)', 'Bash(df:*)',
    # Text processing
    'Bash(cat:*)', 'Bash(head:*)', 'Bash(tail:*)', 'Bash(wc:*)',
    'Bash(sort:*)', 'Bash(uniq:*)', 'Bash(diff:*)', 'Bash(comm:*)',
    'Bash(sed:*)', 'Bash(awk:*)', 'Bash(tr:*)', 'Bash(cut:*)', 'Bash(paste:*)',
    'Bash(grep:*)', 'Bash(egrep:*)', 'Bash(fgrep:*)', 'Bash(rg:*)',
    'Bash(xargs:*)', 'Bash(tee:*)', 'Bash(rev:*)', 'Bash(fold:*)',
    # Output
    'Bash(echo:*)', 'Bash(printf:*)', 'Bash(yes:*)',
    # Languages
    'Bash(python3:*)', 'Bash(python:*)', 'Bash(node:*)', 'Bash(npx:*)',
    'Bash(ruby:*)', 'Bash(perl:*)', 'Bash(php:*)', 'Bash(bash:*)', 'Bash(sh:*)',
    # Package managers
    'Bash(pip:*)', 'Bash(pip3:*)', 'Bash(npm:*)', 'Bash(yarn:*)', 'Bash(pnpm:*)',
    # Network / HTTP
    'Bash(curl:*)', 'Bash(wget:*)', 'Bash(http:*)',
    # Archives
    'Bash(tar:*)', 'Bash(gzip:*)', 'Bash(gunzip:*)', 'Bash(bzip2:*)',
    'Bash(zip:*)', 'Bash(unzip:*)', 'Bash(7z:*)', 'Bash(xz:*)',
    # Image / audio / video
    'Bash(convert:*)', 'Bash(identify:*)', 'Bash(mogrify:*)', 'Bash(composite:*)',
    'Bash(ffmpeg:*)', 'Bash(ffprobe:*)', 'Bash(sox:*)', 'Bash(soxi:*)',
    'Bash(aplay:*)', 'Bash(arecord:*)', 'Bash(lame:*)', 'Bash(oggenc:*)',
    'Bash(magick:*)', 'Bash(gifsicle:*)', 'Bash(optipng:*)', 'Bash(pngquant:*)',
    # Data / encoding
    'Bash(jq:*)', 'Bash(base64:*)', 'Bash(md5sum:*)', 'Bash(sha256sum:*)',
    'Bash(openssl:*)', 'Bash(xxd:*)', 'Bash(od:*)',
    # System info (read-only)
    'Bash(date:*)', 'Bash(env:*)', 'Bash(which:*)', 'Bash(whoami:*)',
    'Bash(hostname:*)', 'Bash(uname:*)', 'Bash(id:*)', 'Bash(test:*)',
    'Bash(true:*)', 'Bash(false:*)', 'Bash(sleep:*)',
    # Git
    'Bash(git:*)',
    # Web tools
    'WebFetch', 'WebSearch',
]


def _build_system_prompt(artist_root: Path) -> str:
    """Build the platform context that gets appended to Claude Code's
    default system prompt — same docs the legacy claude-stream code fed
    in, plus this artist's config and page tree.
    """
    parts: list[str] = []

    if _DOCS_DIR.exists():
        for f in sorted(_DOCS_DIR.glob('[0-9]*.md')):
            try:
                parts.append(f.read_text(encoding='utf-8'))
            except OSError:
                pass

    cfg = artist_root / 'config.json'
    if cfg.exists():
        try:
            parts.append(
                '## This artist (config.json)\n\n```json\n'
                + cfg.read_text(encoding='utf-8') + '\n```'
            )
        except OSError:
            pass

    excluded = {'assets', '.snapshots', '__pycache__', 'backups', 'widgets'}
    pages: list[str] = []
    for d in sorted(artist_root.iterdir()):
        if d.is_dir() and d.name not in excluded and not d.name.startswith('.'):
            if (d / 'content.md').exists():
                pages.append(d.name)
    if pages:
        page_list = '\n'.join(f'- `{p}/content.md` and `{p}/config.json`' for p in pages)
        parts.append(
            '## Pages in this site\n\n' + page_list +
            '\n\nUse the Read tool to view any file before editing. After'
            ' edits, tell the user to click **Save** in the dashboard to'
            ' compile and publish.'
        )

    return '\n\n---\n\n'.join(parts)


class ClaudeSession:
    def __init__(self, artist_slug: str, artist_root: Path, sid: str):
        self.artist_slug = artist_slug
        self.artist_root = artist_root
        self.sid = sid
        self.proc: subprocess.Popen | None = None
        self.master_fd: int | None = None
        self._lock = threading.Lock()

    def start(self, socketio) -> None:
        master, slave = pty.openpty()
        self.master_fd = master

        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['COLUMNS'] = '120'
        env['LINES'] = '40'
        # Don't inherit a stale "I'm running inside Claude Code" marker —
        # would confuse the spawned instance about its parent context.
        env.pop('CLAUDECODE', None)

        try:
            sys_prompt = _build_system_prompt(self.artist_root)
        except Exception:
            sys_prompt = ''

        # --permission-mode acceptEdits: auto-accept file edits inside the
        # cwd (the artist directory). bypassPermissions mode is gated under
        # the same root-refusal as --dangerously-skip-permissions, so we
        # use the next-best mode and let the bridge auto-dismiss the
        # workspace-trust dialog by sending "\r" right after spawn (default
        # button is "Yes, proceed"). Safety: ALLOWED_TOOLS curates Bash.
        cmd = [
            'claude',
            '--permission-mode', 'acceptEdits',
        ]
        if sys_prompt:
            cmd.extend(['--append-system-prompt', sys_prompt])
        cmd.extend(['--allowedTools', *ALLOWED_TOOLS])

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=slave, stdout=slave, stderr=slave,
                cwd=str(self.artist_root),
                env=env,
                close_fds=True,
                preexec_fn=os.setsid,
            )
        except FileNotFoundError:
            try:
                os.write(master, b"\r\n[adze] claude binary not found at /usr/local/bin/claude.\r\n")
            except OSError:
                pass
            os.close(slave)
            return
        finally:
            try:
                os.close(slave)
            except OSError:
                pass

        _log.info(f'[{self.artist_slug}] claude session start sid={self.sid} pid={self.proc.pid}')

        # Auto-dismiss the workspace-trust dialog ("Do you trust the files
        # in this folder? 1) Yes, proceed"). Default selection is option 1
        # so bare \r accepts. We send a few times across the first ~3s
        # since the exact moment the dialog is ready to read input depends
        # on claude's startup speed. Harmless if the dialog didn't fire —
        # claude's main prompt swallows empty Enter as a no-op.
        import time as _t
        def _dismiss_trust():
            for delay in (0.8, 1.5, 2.5):
                _t.sleep(delay if delay == 0.8 else (delay - (delay - 0.7)))
                if self.master_fd is None:
                    return
                try:
                    os.write(self.master_fd, b'\r')
                except OSError:
                    return
        threading.Thread(target=_dismiss_trust, daemon=True).start()

        def reader():
            try:
                while True:
                    try:
                        data = os.read(self.master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    socketio.emit(
                        'aider:output',
                        data.decode('utf-8', errors='replace'),
                        to=self.sid,
                        namespace='/aider',
                    )
            finally:
                _log.info(f'[{self.artist_slug}] claude reader exit sid={self.sid}')
                socketio.emit('aider:exit', {}, to=self.sid, namespace='/aider')

        socketio.start_background_task(reader)

    def write(self, data: str) -> None:
        with self._lock:
            if self.master_fd is not None:
                try:
                    os.write(self.master_fd, data.encode('utf-8'))
                except OSError:
                    pass

    def resize(self, cols: int, rows: int) -> None:
        with self._lock:
            if self.master_fd is not None:
                try:
                    fcntl.ioctl(
                        self.master_fd,
                        termios.TIOCSWINSZ,
                        struct.pack('HHHH', rows, cols, 0, 0),
                    )
                except OSError:
                    pass

    def stop(self) -> None:
        with self._lock:
            if self.proc and self.proc.poll() is None:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                    try:
                        self.proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                except ProcessLookupError:
                    pass
            if self.master_fd is not None:
                try:
                    os.close(self.master_fd)
                except OSError:
                    pass
                self.master_fd = None
            _log.info(f'[{self.artist_slug}] claude session stop sid={self.sid}')


# Per-Socket.IO-session-id registry. One claude process per browser tab.
_sessions: dict[str, ClaudeSession] = {}
_sessions_lock = threading.Lock()


def register(socketio) -> None:
    """Register Socket.IO event handlers on the /aider namespace.

    The namespace name is kept as `/aider` (rather than renamed to
    /claude or /vibe) so the dashboard's existing client code keeps
    working without changes. The handler internals are Claude.
    """

    @socketio.on('connect', namespace='/aider')
    def on_connect(auth):
        # Auth strategy: try the auth payload first (X-Admin-Token-style direct
        # login). Fall back to the adze_session cookie.
        auth = auth if isinstance(auth, dict) else {}
        artist_slug = auth.get('artist_slug') or ''
        token = auth.get('token') or ''

        ok = False
        if artist_slug and token and _verify(artist_slug, token):
            ok = True
        else:
            session_cookie = request.cookies.get('adze_session', '')
            if session_cookie and ':' in session_cookie:
                cslug, _, ctok = session_cookie.partition(':')
                if cslug and _verify(cslug, ctok):
                    artist_slug = cslug
                    ok = True

        if not ok or not artist_slug:
            _log.warning(f'claude connect: auth failed (slug={artist_slug!r}, has_token={bool(token)})')
            return False

        artist_root = (Path.cwd() / 'artists' / artist_slug).resolve()
        if not artist_root.exists():
            _log.warning(f'claude connect: artist root missing {artist_root}')
            return False

        sid = request.sid
        sess = ClaudeSession(artist_slug, artist_root, sid)
        with _sessions_lock:
            _sessions[sid] = sess
        sess.start(socketio)
        return True

    @socketio.on('aider:input', namespace='/aider')
    def on_input(data):
        sid = request.sid
        with _sessions_lock:
            sess = _sessions.get(sid)
        if sess and isinstance(data, dict):
            sess.write(data.get('data', ''))

    @socketio.on('aider:resize', namespace='/aider')
    def on_resize(data):
        sid = request.sid
        with _sessions_lock:
            sess = _sessions.get(sid)
        if sess and isinstance(data, dict):
            try:
                cols = int(data.get('cols', 80))
                rows = int(data.get('rows', 24))
                sess.resize(cols, rows)
            except (TypeError, ValueError):
                pass

    @socketio.on('disconnect', namespace='/aider')
    def on_disconnect():
        sid = request.sid
        with _sessions_lock:
            sess = _sessions.pop(sid, None)
        if sess:
            sess.stop()
