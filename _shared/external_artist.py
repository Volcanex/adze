"""External (remote) artist support — config and manifest helpers.

An artist is "external" when its `artists/<slug>/config.json` carries a
`remote` block:

    {
      "remote": {
        "host": "alias-or-user@host",
        "path": "/abs/path/to/seed/repo",
        "key": "ssh_key"
      }
    }

`host` is anything `ssh` accepts (an `~/.ssh/config` alias works).
`path` is the absolute path to the Seed repo on the remote box.
`key` is relative to the artist dir (default `ssh_key`).

The manifest (`.adze-remote.json` at the remote repo root) is fetched
fresh each time and cached at `artists/<slug>/.adze-remote.cache.json`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


MANIFEST_FILENAME = ".adze-remote.json"
MANIFEST_CACHE = ".adze-remote.cache.json"

DEFAULT_BUILD_COMMAND = "python3 compile.py"
DEFAULT_BUILD_ON = "agent"
DEFAULT_README_PATH = "CLAUDE.md"


def _artist_config_path(slug: str) -> Path:
    return Path(f"artists/{slug}/config.json")


def _load_artist_config(slug: str) -> dict:
    path = _artist_config_path(slug)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def is_remote(slug: str) -> bool:
    cfg = _load_artist_config(slug)
    remote = cfg.get("remote")
    return isinstance(remote, dict) and bool(remote.get("host")) and bool(remote.get("path"))


def load_remote_config(slug: str) -> Optional[dict]:
    """Return the `remote` block (host, path, key) or None if not external.

    `key` is resolved to an absolute path under the artist dir.
    """
    cfg = _load_artist_config(slug)
    remote = cfg.get("remote")
    if not isinstance(remote, dict):
        return None
    host = remote.get("host")
    path = remote.get("path")
    if not host or not path:
        return None
    key_rel = remote.get("key", "ssh_key")
    key_path = Path(f"artists/{slug}") / key_rel
    return {
        "host": host,
        "path": path,
        "key": str(key_path),
    }


def manifest_defaults(slug: str) -> dict:
    """Defaults used when `.adze-remote.json` is absent or malformed.

    `preview_url` is derived from the artist's local `config.json:domain`
    when set, otherwise empty.
    """
    cfg = _load_artist_config(slug)
    domain = cfg.get("domain") or ""
    preview_url = f"https://{domain}" if domain else ""
    return {
        "preview_url": preview_url,
        "build_command": DEFAULT_BUILD_COMMAND,
        "build_on": DEFAULT_BUILD_ON,
        "readme_path": DEFAULT_README_PATH,
        "client_brief": "",
    }


def merge_manifest(slug: str, raw: dict) -> dict:
    """Overlay a raw manifest dict onto the defaults for this artist."""
    merged = manifest_defaults(slug)
    if isinstance(raw, dict):
        for key in ("preview_url", "build_command", "build_on", "readme_path", "client_brief"):
            value = raw.get(key)
            if isinstance(value, str) and value:
                merged[key] = value
    return merged


def cache_manifest(slug: str, manifest: dict) -> None:
    """Persist the resolved manifest for the session."""
    cache_path = Path(f"artists/{slug}/{MANIFEST_CACHE}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(manifest, indent=2))


def cached_manifest(slug: str) -> Optional[dict]:
    cache_path = Path(f"artists/{slug}/{MANIFEST_CACHE}")
    if not cache_path.exists():
        return None
    try:
        return json.loads(cache_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
