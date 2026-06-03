"""
Per-artist sandbox container helpers.

The Adze platform runs a single sandbox container per artist
(`adze-terminal-<slug>`) shared between Terminal Access and Auto-Code.
This module centralises the naming, network, volume, and lifecycle
logic so both subsystems agree on which container they're talking to.

Historically the helpers were duplicated in `terminal_bridge.py` and
`auto_code_bridge.py`. New code imports from here; the older copies
remain in place until their owners migrate, to keep the blast radius
of this change tight.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path

_log = logging.getLogger('adze.sandbox')


def safe_slug(artist_slug: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '-', artist_slug).strip('-').lower() or 'artist'


def terminal_container_name(artist_slug: str) -> str:
    return f'adze-terminal-{safe_slug(artist_slug)}'


def terminal_auth_volume(artist_slug: str) -> str:
    return f'adze_terminal_claude_{safe_slug(artist_slug)}'


def docker_network() -> str:
    return os.environ.get('ADZE_TERMINAL_NETWORK', 'adze_default')


def docker_image() -> str:
    return os.environ.get('ADZE_TERMINAL_IMAGE', 'adze-terminal:latest')


def host_artist_root(artist_slug: str) -> Path:
    host_root = Path(os.environ.get('ADZE_HOST_ROOT', Path.cwd()))
    return (host_root / 'artists' / artist_slug).resolve()


def docker(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ['docker', *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )


def ensure_terminal_container(artist_slug: str) -> str:
    """Create or start the per-artist sandbox container, returning its name."""
    container_name = terminal_container_name(artist_slug)
    inspect = docker('container', 'inspect', container_name, check=False)
    if inspect.returncode != 0:
        run = docker(
            'run', '-d',
            '--name', container_name,
            '--label', 'adze.terminal=1',
            '--label', f'adze.artist_slug={artist_slug}',
            '--network', docker_network(),
            '--workdir', '/workspace',
            '--user', '1000:1000',
            '--env', 'HOME=/home/adze',
            '--env', 'SHELL=/bin/bash',
            '--mount', f'type=bind,src={host_artist_root(artist_slug)},dst=/workspace',
            '--mount', f'type=volume,src={terminal_auth_volume(artist_slug)},dst=/home/adze/.claude',
            '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges',
            '--pids-limit', '256',
            '--memory', os.environ.get('ADZE_TERMINAL_MEMORY', '2g'),
            '--cpus', os.environ.get('ADZE_TERMINAL_CPUS', '2'),
            docker_image(),
        )
        _log.info(f'[{artist_slug}] created sandbox {container_name}: {run.stdout.strip()}')
    else:
        state = docker('inspect', '-f', '{{.State.Running}}', container_name, check=False)
        if state.returncode == 0 and state.stdout.strip() != 'true':
            docker('start', container_name)

    return container_name


def list_running_sandboxes() -> list[str]:
    """Return container names of every running adze-terminal-* sandbox."""
    r = docker('ps', '--filter', 'label=adze.terminal=1', '--format', '{{.Names}}', check=False)
    if r.returncode != 0:
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]
