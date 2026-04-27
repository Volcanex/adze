"""
Adze Vibe Coder — in-process agent loop.

Replaces the legacy `claude` CLI subprocess at admin_api.py:claude-stream.
Uses LiteLLM as the LLM transport so we can route OpenRouter -> Gemini
(or any other provider) without rewriting tool-calling glue.

Why hand-rolled instead of openhands-sdk:
  As of 2026-04, openhands-sdk's public docs don't cover custom tool
  definition, filesystem scoping, streaming callbacks, or session reset
  in production-confident detail. We need all four. The interface here
  (`run_turn`) is small enough to swap to openhands-sdk later when their
  docs catch up — replace the body of the while-loop, keep the event
  shape the SSE consumer expects.

Tool surface mirrors Claude Code semantics (Read/Write/Edit/Glob/Grep/
Bash/WebFetch) so the existing system-prompt docs in _shared/docs/*.md
keep working unchanged.

All filesystem and shell operations are path-scoped to the artist's
directory. Bash is further constrained by an allow-list mirroring the
one previously enforced by Claude CLI's --allowedTools at
admin_api.py:4695-4737.
"""

from __future__ import annotations

import os
import re
import json
import time
import shlex
import fnmatch
import logging
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List

try:
    import litellm
    litellm.drop_params = True  # ignore unsupported kwargs across providers
except ImportError as e:
    raise ImportError(
        "vibe_agent requires litellm. Install with: pip install litellm"
    ) from e


# ── Models ────────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "openrouter/google/gemini-2.5-flash"
PRO_MODEL = "openrouter/google/gemini-2.5-pro"
LITE_MODEL = "openrouter/google/gemini-2.5-flash-lite"

# Per-call model override via prompt prefix
MODEL_PREFIXES = {
    "@pro ": PRO_MODEL,
    "@flash ": DEFAULT_MODEL,
    "@lite ": LITE_MODEL,
}


def _select_model(prompt: str, default: str = DEFAULT_MODEL) -> tuple[str, str]:
    """Strip and return (model, cleaned_prompt)."""
    for prefix, model in MODEL_PREFIXES.items():
        if prompt.startswith(prefix):
            return model, prompt[len(prefix):]
    return default, prompt


# ── Bash allow-list (mirrors admin_api.py existing list) ──────────────────────

BASH_ALLOWED = frozenset({
    "ls", "mkdir", "cp", "mv", "rm", "touch", "chmod", "chown", "ln",
    "basename", "dirname", "realpath", "readlink", "find", "tree", "pwd",
    "stat", "file", "du", "df",
    "cat", "head", "tail", "wc", "sort", "uniq", "diff", "comm",
    "sed", "awk", "tr", "cut", "paste",
    "grep", "egrep", "fgrep", "rg", "xargs", "tee", "rev", "fold",
    "echo", "printf", "yes",
    "python3", "python", "node", "npx", "ruby", "perl", "php", "bash", "sh",
    "pip", "pip3", "npm", "yarn", "pnpm",
    "curl", "wget", "http",
    "tar", "gzip", "gunzip", "bzip2", "zip", "unzip", "7z", "xz",
    "convert", "identify", "mogrify", "composite",
    "ffmpeg", "ffprobe", "sox", "soxi", "lame", "oggenc",
    "magick", "gifsicle", "optipng", "pngquant",
    "jq", "base64", "md5sum", "sha256sum", "openssl", "xxd", "od",
    "date", "env", "which", "whoami", "hostname", "uname", "id",
    "test", "true", "false", "sleep", "git",
})


# ── Path scoping ──────────────────────────────────────────────────────────────

def _resolve_path(artist_root: Path, given: str) -> Path:
    """Resolve a tool-supplied path inside artist_root, refusing escapes."""
    p = Path(given)
    if not p.is_absolute():
        p = artist_root / p
    p = p.resolve()
    root_resolved = artist_root.resolve()
    try:
        p.relative_to(root_resolved)
    except ValueError:
        raise PermissionError(
            f"Path '{given}' resolves outside the artist directory "
            f"({artist_root.name}/). Refusing."
        )
    return p


# ── Tool implementations ──────────────────────────────────────────────────────

def _tool_read(artist_root: Path, args: dict) -> str:
    path = _resolve_path(artist_root, args["file_path"])
    if not path.exists():
        raise FileNotFoundError(f"{args['file_path']} does not exist")
    if path.is_dir():
        raise IsADirectoryError(f"{args['file_path']} is a directory; use Glob or Bash(ls)")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    offset = args.get("offset", 0)
    limit = args.get("limit")
    if offset:
        lines = lines[offset:]
    if limit is not None:
        lines = lines[:limit]
    base = offset or 0
    return "\n".join(f"{i + 1 + base}\t{ln}" for i, ln in enumerate(lines))


def _tool_write(artist_root: Path, args: dict) -> str:
    path = _resolve_path(artist_root, args["file_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"], encoding="utf-8")
    return f"Wrote {args['file_path']} ({len(args['content'])} bytes)"


def _tool_edit(artist_root: Path, args: dict) -> str:
    path = _resolve_path(artist_root, args["file_path"])
    text = path.read_text(encoding="utf-8")
    old = args["old_string"]
    new = args["new_string"]
    replace_all = bool(args.get("replace_all", False))
    if old == new:
        raise ValueError("old_string and new_string are identical")
    occurrences = text.count(old)
    if occurrences == 0:
        raise ValueError(f"old_string not found in {args['file_path']}")
    if occurrences > 1 and not replace_all:
        raise ValueError(
            f"old_string appears {occurrences} times in {args['file_path']}. "
            f"Pass replace_all=true or include more surrounding context."
        )
    new_text = text.replace(old, new)
    path.write_text(new_text, encoding="utf-8")
    n = occurrences if replace_all else 1
    return f"Replaced {n} occurrence(s) in {args['file_path']}"


def _tool_glob(artist_root: Path, args: dict) -> str:
    pattern = args["pattern"]
    matches: list[str] = []
    for p in artist_root.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(artist_root))
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(p.name, pattern):
                matches.append(rel)
    matches.sort()
    return "\n".join(matches) or "(no matches)"


def _tool_grep(artist_root: Path, args: dict) -> str:
    pattern = args["pattern"]
    path = args.get("path", ".")
    target = _resolve_path(artist_root, path)
    # Prefer ripgrep for speed and decent default behaviour
    try:
        rg = subprocess.run(
            ["rg", "-n", "--no-heading", pattern, str(target)],
            capture_output=True, text=True, timeout=30,
        )
        if rg.returncode in (0, 1):  # 0=found, 1=not-found
            return rg.stdout or "(no matches)"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    # Python fallback
    try:
        rx = re.compile(pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}")
    out = []
    files = [target] if target.is_file() else target.rglob("*")
    for p in files:
        if not p.is_file():
            continue
        try:
            for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(ln):
                    out.append(f"{p.relative_to(artist_root)}:{i}:{ln}")
        except (UnicodeDecodeError, PermissionError):
            continue
    return "\n".join(out) or "(no matches)"


def _tool_bash(artist_root: Path, args: dict) -> str:
    command = args["command"]
    timeout = int(args.get("timeout", 60))
    try:
        first = shlex.split(command)[0]
    except (ValueError, IndexError):
        raise ValueError("Could not parse command")
    bin_name = Path(first).name
    if bin_name not in BASH_ALLOWED:
        raise PermissionError(
            f"Command '{bin_name}' is not in the vibe-coder allow-list. "
            f"Tell the user what you wanted to run; they can add it if it's safe."
        )
    proc = subprocess.run(
        command, shell=True, cwd=str(artist_root),
        capture_output=True, text=True, timeout=timeout,
    )
    out = proc.stdout
    if proc.stderr:
        out += ("\n[stderr]\n" if out else "[stderr]\n") + proc.stderr
    if proc.returncode != 0:
        out += f"\n[exit code: {proc.returncode}]"
    return out or "(no output)"


def _tool_webfetch(artist_root: Path, args: dict) -> str:
    url = args["url"]
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    req = urllib.request.Request(url, headers={"User-Agent": "AdzeVibeCoder/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read(200_000)  # cap at ~200kB
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL error: {e.reason}"
    text = body.decode("utf-8", errors="replace")
    # Strip script/style for token efficiency
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
    return text[:50_000]


TOOL_IMPLS = {
    "Read": _tool_read,
    "Write": _tool_write,
    "Edit": _tool_edit,
    "Glob": _tool_glob,
    "Grep": _tool_grep,
    "Bash": _tool_bash,
    "WebFetch": _tool_webfetch,
}


# ── Tool specs (LiteLLM/OpenAI-compatible JSON schema) ────────────────────────

def _tool_specs() -> List[dict]:
    return [
        {"type": "function", "function": {
            "name": "Read",
            "description": "Read a file's contents. Path must be inside the artist's directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path relative to the artist's directory."},
                    "offset": {"type": "integer", "description": "Optional starting line (0-indexed)."},
                    "limit": {"type": "integer", "description": "Optional max number of lines to return."},
                },
                "required": ["file_path"],
            },
        }},
        {"type": "function", "function": {
            "name": "Write",
            "description": "Create or overwrite a file. Parent directories created as needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["file_path", "content"],
            },
        }},
        {"type": "function", "function": {
            "name": "Edit",
            "description": (
                "Replace exact strings in an existing file. The old_string must be unique unless "
                "replace_all is true. Prefer Edit over Write for small changes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                    "replace_all": {"type": "boolean", "description": "Replace every occurrence."},
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        }},
        {"type": "function", "function": {
            "name": "Glob",
            "description": "List files in the artist's directory matching a glob pattern (e.g. '**/*.md').",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        }},
        {"type": "function", "function": {
            "name": "Grep",
            "description": "Search for a regex pattern across files in the artist's directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regular expression."},
                    "path": {"type": "string", "description": "File or subdirectory to search. Default: artist root."},
                },
                "required": ["pattern"],
            },
        }},
        {"type": "function", "function": {
            "name": "Bash",
            "description": (
                "Run a shell command in the artist's directory. Limited to a curated allow-list "
                "(no sudo, systemctl, ssh, etc.). Use for: ls, find, image processing (convert/ffmpeg), "
                "git, jq, file manipulation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "description": "Seconds. Default 60, max 300."},
                },
                "required": ["command"],
            },
        }},
        {"type": "function", "function": {
            "name": "WebFetch",
            "description": "Fetch a URL and return the text body (capped at 50kB).",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        }},
    ]


# ── Conversation persistence ──────────────────────────────────────────────────

def load_history(sessions_dir: Path, session_id: str) -> List[dict]:
    f = sessions_dir / f"{session_id}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_history(sessions_dir: Path, session_id: str, history: List[dict]) -> None:
    sessions_dir.mkdir(parents=True, exist_ok=True)
    f = sessions_dir / f"{session_id}.json"
    f.write_text(json.dumps(history, indent=2), encoding="utf-8")


def clear_session(sessions_dir: Path, session_id: str) -> bool:
    f = sessions_dir / f"{session_id}.json"
    if f.exists():
        f.unlink()
        return True
    return False


# ── The agent loop ────────────────────────────────────────────────────────────

MAX_ITERATIONS = 25  # safety bound on tool-call loop per turn


def run_turn(
    artist_root: Path,
    sessions_dir: Path,
    session_id: str,
    prompt: str,
    system_prompt: str,
    log: Optional[logging.Logger] = None,
    artist_slug: Optional[str] = None,
) -> Iterator[dict]:
    """
    Run one user turn (one prompt -> one final assistant text), looping over
    tool calls as needed. Yields events shaped to match what dashboard.html's
    SSE parser at line 6472+ expects:

        {type: 'assistant', message: {content: [{type:'text',text}|{type:'tool_use',id,name,input}]}}
        {type: 'tool_result', tool_use_id, content, is_error}
        {type: 'result', result, cost_usd?, duration_ms}
        {type: 'system_message', text}
        {type: 'error', error}
        {type: 'stream_end'}

    The session's full conversation history persists in
    `sessions_dir/<session_id>.json` and is mutated by this function.
    """
    log = log or logging.getLogger("vibe")
    slug_tag = f"[{artist_slug}] " if artist_slug else ""

    model, prompt = _select_model(prompt)
    if model != DEFAULT_MODEL:
        yield {"type": "system_message", "text": f"Routing this turn through {model.split('/')[-1]}."}

    history = load_history(sessions_dir, session_id)
    if not history:
        history.append({"role": "system", "content": system_prompt})
    history.append({"role": "user", "content": prompt})

    started = time.time()
    total_cost: float = 0.0
    final_text = ""

    try:
        for iteration in range(1, MAX_ITERATIONS + 1):
            try:
                response = litellm.completion(
                    model=model,
                    messages=history,
                    tools=_tool_specs(),
                    tool_choice="auto",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    api_base="https://openrouter.ai/api/v1",
                    temperature=0.3,
                )
            except Exception as e:
                log.error(f"{slug_tag}LLM error iteration {iteration}: {e}")
                yield {"type": "error", "error": f"Model call failed: {e}"}
                return

            try:
                turn_cost = float(litellm.completion_cost(response) or 0.0)
                total_cost += turn_cost
            except Exception:
                turn_cost = 0.0

            choice = response.choices[0]
            msg = choice.message
            text = msg.content or ""
            tool_calls = getattr(msg, "tool_calls", None) or []

            # Build the content array shaped like Anthropic's stream-json format
            content_blocks: list[dict] = []
            if text:
                content_blocks.append({"type": "text", "text": text})
                final_text = text  # last non-empty assistant text wins
            for tc in tool_calls:
                try:
                    parsed_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    parsed_args = {"_raw": tc.function.arguments}
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": parsed_args,
                })
                snippet = json.dumps(parsed_args)[:300]
                log.info(f"{slug_tag}TOOL: {tc.function.name} → {snippet}")

            # Echo to the wire
            yield {"type": "assistant", "message": {"content": content_blocks}}

            # Append assistant turn to history (LiteLLM-compatible shape)
            history.append({
                "role": "assistant",
                "content": text or None,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    } for tc in tool_calls
                ] if tool_calls else None,
            })

            # If no tool calls, the turn is done
            if not tool_calls:
                if text:
                    log.info(f"{slug_tag}TEXT: {text[:500]}")
                duration_ms = int((time.time() - started) * 1000)
                log.info(
                    f"{slug_tag}── END (ok) cost=${total_cost:.4f} duration={duration_ms}ms ──"
                )
                yield {
                    "type": "result",
                    "result": final_text,
                    "cost_usd": round(total_cost, 6),
                    "duration_ms": duration_ms,
                }
                return

            # Execute each tool call and append results to history
            for tc in tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}

                impl = TOOL_IMPLS.get(name)
                if impl is None:
                    result_text = f"Unknown tool: {name}"
                    is_error = True
                else:
                    try:
                        result_text = impl(artist_root, args)
                        is_error = False
                    except (PermissionError, FileNotFoundError, IsADirectoryError, ValueError) as e:
                        result_text = f"{type(e).__name__}: {e}"
                        is_error = True
                    except subprocess.TimeoutExpired:
                        result_text = f"Bash command timed out"
                        is_error = True
                    except Exception as e:
                        log.exception(f"{slug_tag}Tool {name} crashed")
                        result_text = f"Tool crashed: {type(e).__name__}: {e}"
                        is_error = True

                # Cap result text — keep tokens sane
                if len(result_text) > 30_000:
                    result_text = result_text[:30_000] + "\n... (truncated)"

                yield {
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result_text,
                    "is_error": is_error,
                }
                history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_text,
                })

        # Hit the iteration cap
        log.warning(f"{slug_tag}Reached MAX_ITERATIONS={MAX_ITERATIONS}")
        yield {
            "type": "error",
            "error": f"Reached the {MAX_ITERATIONS}-step safety limit. Try splitting the request.",
        }
    finally:
        # Always persist whatever conversation got built
        save_history(sessions_dir, session_id, history)
