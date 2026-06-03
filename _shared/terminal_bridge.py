"""
Terminal Access over WebSocket — tmux/pty bridge.

Each connected dashboard tab attaches to a tmux shell inside a per-artist
Docker sandbox, streamed bidirectionally via Socket.IO.
The frontend renders the stream via xterm.js; UI buttons (Asset / Pointer
/ +) inject text into the pty.

The sandbox mounts only the selected artist directory at /workspace.
Developers can run `claude` themselves after the shell is usable.
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
import re
import shlex
import shutil
from pathlib import Path
from flask import request


def _verify(artist_slug: str, token: str) -> bool:
    from auth import verify_artist_token
    return verify_artist_token(artist_slug, token)


def _is_super_admin_token(token: str) -> bool:
    from auth import is_admin_token
    return is_admin_token(token)


def _artist_exists(artist_slug: str) -> bool:
    if not artist_slug:
        return False
    try:
        return (Path.cwd() / 'artists' / artist_slug).resolve().exists()
    except OSError:
        return False


_log = logging.getLogger('adze.claude')


# Where the platform's Terminal Access docs live — fed to Claude as the
# system prompt so it understands Adze conventions.
_DOCS_DIR = Path(__file__).parent / 'docs'


def _tmux_session_name(artist_slug: str) -> str:
    safe = re.sub(r'[^A-Za-z0-9_.-]+', '-', artist_slug).strip('-')
    return f'adze-{safe or "artist"}'


def _terminal_container_name(artist_slug: str) -> str:
    safe = re.sub(r'[^A-Za-z0-9_.-]+', '-', artist_slug).strip('-').lower()
    return f'adze-terminal-{safe or "artist"}'


def _terminal_auth_volume(artist_slug: str) -> str:
    safe = re.sub(r'[^A-Za-z0-9_.-]+', '-', artist_slug).strip('-').lower()
    return f'adze_terminal_claude_{safe or "artist"}'


def _docker_network() -> str:
    return os.environ.get('ADZE_TERMINAL_NETWORK', 'adze_default')


def _docker_image() -> str:
    return os.environ.get('ADZE_TERMINAL_IMAGE', 'adze-terminal:latest')


def _host_artist_root(artist_slug: str) -> Path:
    host_root = Path(os.environ.get('ADZE_HOST_ROOT', Path.cwd()))
    return (host_root / 'artists' / artist_slug).resolve()


def _docker(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ['docker', *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )


def _ensure_terminal_container(artist_slug: str, artist_root: Path) -> str:
    """Create/start the per-artist terminal sandbox container."""
    container_name = _terminal_container_name(artist_slug)
    inspect = _docker('container', 'inspect', container_name, check=False)
    if inspect.returncode != 0:
        host_artist_root = _host_artist_root(artist_slug)
        run = _docker(
            'run', '-d',
            '--name', container_name,
            '--label', 'adze.terminal=1',
            '--label', f'adze.artist_slug={artist_slug}',
            '--network', _docker_network(),
            '--workdir', '/workspace',
            '--user', '1000:1000',
            '--env', 'HOME=/home/adze',
            '--env', 'SHELL=/bin/bash',
            '--mount', f'type=bind,src={host_artist_root},dst=/workspace',
            '--mount', f'type=volume,src={_terminal_auth_volume(artist_slug)},dst=/home/adze/.claude',
            '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges',
            '--pids-limit', '256',
            '--memory', os.environ.get('ADZE_TERMINAL_MEMORY', '2g'),
            '--cpus', os.environ.get('ADZE_TERMINAL_CPUS', '2'),
            _docker_image(),
        )
        _log.info(f'[{artist_slug}] created terminal sandbox {container_name}: {run.stdout.strip()}')
    else:
        state = _docker('inspect', '-f', '{{.State.Running}}', container_name, check=False)
        if state.returncode == 0 and state.stdout.strip() != 'true':
            _docker('start', container_name)

    return container_name


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

        # Initial PTY window size — otherwise Claude Code's TUI launches at 0x0
        # and never redraws cleanly. Client refines via terminal:resize.
        try:
            fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack('HHHH', 50, 200, 0, 0))
        except OSError:
            pass

        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['COLUMNS'] = '200'
        env['LINES'] = '50'
        # Don't inherit a stale "I'm running inside Claude Code" marker —
        # would confuse the spawned instance about its parent context.
        env.pop('CLAUDECODE', None)

        session_name = _tmux_session_name(self.artist_slug)
        if not shutil.which('docker'):
            try:
                os.write(master, b"\r\n[adze] docker CLI not found. Rebuild the Adze Flask container.\r\n")
            except OSError:
                pass
            os.close(slave)
            return
        try:
            container_name = _ensure_terminal_container(self.artist_slug, self.artist_root)
        except subprocess.CalledProcessError as exc:
            err = (exc.stderr or exc.stdout or str(exc)).strip()
            try:
                os.write(master, f"\r\n[adze] failed to create terminal sandbox: {err}\r\n".encode('utf-8'))
            except OSError:
                pass
            os.close(slave)
            return
        except Exception as exc:
            try:
                os.write(master, f"\r\n[adze] failed to create terminal sandbox: {exc}\r\n".encode('utf-8'))
            except OSError:
                pass
            os.close(slave)
            return
        shell_cmd = (
            'export HOME=/home/adze SHELL=/bin/bash ADZE_ARTIST_SLUG='
            + shlex.quote(self.artist_slug)
            + '; exec /usr/local/bin/adze-shell'
        )
        tmux_cmd = [
            'docker', 'exec', '-it',
            '--user', '1000:1000',
            '--env', 'HOME=/home/adze',
            '--env', 'SHELL=/bin/bash',
            '--workdir', '/workspace',
            container_name,
            'tmux', 'new-session',
            '-A',
            '-s', 'terminal',
            '-c', '/workspace',
            shell_cmd,
        ]

        try:
            self.proc = subprocess.Popen(
                tmux_cmd,
                stdin=slave, stdout=slave, stderr=slave,
                cwd=str(self.artist_root),
                env=env,
                close_fds=True,
                preexec_fn=os.setsid,
            )
        except FileNotFoundError:
            try:
                os.write(master, b"\r\n[adze] docker CLI not found. Rebuild the Adze Flask container.\r\n")
            except OSError:
                pass
            os.close(slave)
            return
        finally:
            try:
                os.close(slave)
            except OSError:
                pass

        _log.info(f'[{self.artist_slug}] terminal sandbox attach sid={self.sid} container={container_name} session={session_name} pid={self.proc.pid}')

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
                        'terminal:output',
                        data.decode('utf-8', errors='replace'),
                        to=self.sid,
                        namespace='/terminal',
                    )
            finally:
                _log.info(f'[{self.artist_slug}] terminal reader exit sid={self.sid}')
                socketio.emit('terminal:exit', {}, to=self.sid, namespace='/terminal')

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
            _log.info(f'[{self.artist_slug}] terminal client detached sid={self.sid}')


# Per-Socket.IO-session-id registry. One terminal client per browser tab.
_sessions: dict[str, ClaudeSession] = {}
_sessions_lock = threading.Lock()


def register(socketio) -> None:
    """Register Socket.IO event handlers on the /terminal namespace.

    The `/terminal` namespace carries raw pty input/output for xterm.js.
    """

    @socketio.on('connect', namespace='/terminal')
    def on_connect(auth):
        # Auth strategy: try the auth payload first (X-Admin-Token-style direct
        # login). Fall back to artist or super-admin cookies. Admin Mode uses
        # an httpOnly cookie plus auth.artist_slug, so the token is often blank.
        auth = auth if isinstance(auth, dict) else {}
        artist_slug = auth.get('artist_slug') or ''
        token = auth.get('token') or ''

        ok = False
        if artist_slug and token and _verify(artist_slug, token):
            ok = True
        else:
            admin_cookie = request.cookies.get('adze_admin_session', '')
            if artist_slug and _is_super_admin_token(admin_cookie) and _artist_exists(artist_slug):
                ok = True

            session_cookie = request.cookies.get('adze_session', '')
            if not ok and session_cookie and ':' in session_cookie:
                cslug, _, ctok = session_cookie.partition(':')
                if artist_slug and _is_super_admin_token(ctok) and _artist_exists(artist_slug):
                    ok = True
                elif cslug and _verify(cslug, ctok):
                    artist_slug = cslug
                    ok = True

        if not ok or not artist_slug:
            _log.warning(f'terminal connect: auth failed (slug={artist_slug!r}, has_token={bool(token)})')
            return False

        artist_root = (Path.cwd() / 'artists' / artist_slug).resolve()
        if not artist_root.exists():
            _log.warning(f'terminal connect: artist root missing {artist_root}')
            return False

        sid = request.sid
        sess = ClaudeSession(artist_slug, artist_root, sid)
        with _sessions_lock:
            _sessions[sid] = sess
        sess.start(socketio)
        return True

    @socketio.on('terminal:input', namespace='/terminal')
    def on_input(data):
        sid = request.sid
        with _sessions_lock:
            sess = _sessions.get(sid)
        if sess and isinstance(data, dict):
            sess.write(data.get('data', ''))

    @socketio.on('terminal:resize', namespace='/terminal')
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

    @socketio.on('disconnect', namespace='/terminal')
    def on_disconnect():
        sid = request.sid
        with _sessions_lock:
            sess = _sessions.pop(sid, None)
        if sess:
            sess.stop()
