"""
Aider over WebSocket — pty bridge.

Each connected dashboard tab gets its own `aider` subprocess running inside a
pty, streamed bidirectionally via Socket.IO. The frontend renders the stream
via xterm.js; UI buttons (Asset / Pointer / +) just inject text into the pty.

Why pty instead of wrapping aider's Python API:
  Aider was designed for the terminal — slash commands, prompt-toolkit
  prompts, ANSI rendering, search-replace blocks, /diff /commit /add /drop.
  Wrapping its CLI output in our SSE turn-card format fights the tool. A
  raw pty preserves every aider feature for free, and the dashboard's job
  is reduced to "be a terminal" — which xterm.js does in 50 lines.
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


# Lazy import so aider_bridge.py is importable even before auth.py is set up
def _verify(artist_slug: str, token: str) -> bool:
    from auth import verify_artist_token
    return verify_artist_token(artist_slug, token)


_log = logging.getLogger('adze.aider')


DEFAULT_MODEL = 'openrouter/anthropic/claude-sonnet-4.5'


class AiderSession:
    def __init__(self, artist_slug: str, artist_root: Path, sid: str):
        self.artist_slug = artist_slug
        self.artist_root = artist_root
        self.sid = sid
        self.proc: subprocess.Popen | None = None
        self.master_fd: int | None = None
        self._lock = threading.Lock()

    def start(self, socketio, model: str = DEFAULT_MODEL) -> None:
        master, slave = pty.openpty()
        self.master_fd = master

        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['COLUMNS'] = '120'
        env['LINES'] = '40'
        # OPENROUTER_API_KEY must already be in the container env (forwarded
        # by docker-compose).

        # Block GitPython from walking up past the artist's parent dir. Without
        # this, aider finds /app/.git (the platform repo) and treats /app as
        # the "git working dir", making in-chat filenames resolve from the
        # wrong root. With this, --no-git is fully effective.
        env['GIT_CEILING_DIRECTORIES'] = str(self.artist_root.parent)

        cmd = [
            'aider',
            '--no-git',
            '--no-auto-commits',
            '--no-auto-lint',
            '--stream',
            '--yes-always',
            '--no-show-model-warnings',
            '--model', model,
        ]

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=slave, stdout=slave, stderr=slave,
                cwd=str(self.artist_root),
                env=env,
                close_fds=True,
                preexec_fn=os.setsid,  # new session group → clean killpg
            )
        except FileNotFoundError:
            # aider not installed
            try:
                os.write(master, b"\r\n[adze] aider binary not found. Add aider-chat to requirements.txt and rebuild.\r\n")
            except OSError:
                pass
            os.close(slave)
            return
        finally:
            try:
                os.close(slave)
            except OSError:
                pass

        _log.info(f'[{self.artist_slug}] aider session start sid={self.sid} pid={self.proc.pid}')

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
                _log.info(f'[{self.artist_slug}] aider reader exit sid={self.sid}')
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
            _log.info(f'[{self.artist_slug}] aider session stop sid={self.sid}')


# Per-Socket.IO-session-id registry. One aider process per browser tab.
_sessions: dict[str, AiderSession] = {}
_sessions_lock = threading.Lock()


def register(socketio) -> None:
    """Register Socket.IO event handlers on the /aider namespace."""

    @socketio.on('connect', namespace='/aider')
    def on_connect(auth):
        if not auth or not isinstance(auth, dict):
            _log.warning('aider connect: missing auth payload')
            return False
        artist_slug = auth.get('artist_slug')
        token = auth.get('token')
        if not artist_slug or not _verify(artist_slug, token):
            _log.warning(f'aider connect: auth failed for slug={artist_slug}')
            return False

        artist_root = (Path.cwd() / 'artists' / artist_slug).resolve()
        if not artist_root.exists():
            _log.warning(f'aider connect: artist root missing {artist_root}')
            return False

        sid = request.sid
        sess = AiderSession(artist_slug, artist_root, sid)
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
