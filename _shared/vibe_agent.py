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
import difflib
import fnmatch
import logging
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List, Union

try:
    import litellm
    litellm.drop_params = True  # ignore unsupported kwargs across providers
except ImportError as e:
    raise ImportError(
        "vibe_agent requires litellm. Install with: pip install litellm"
    ) from e


# ── Models ────────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "openrouter/anthropic/claude-sonnet-4.5"
SONNET_MODEL = DEFAULT_MODEL
HAIKU_MODEL = "openrouter/anthropic/claude-haiku-4.5"
PRO_MODEL = "openrouter/google/gemini-2.5-pro"
FLASH_MODEL = "openrouter/google/gemini-2.5-flash"
LITE_MODEL = "openrouter/google/gemini-2.5-flash-lite"

# Per-call model override via prompt prefix.
# Default = Claude Sonnet 4.5 (best tool-call reliability at long context).
# Cheap escape hatches stay available:
#   @haiku  — Claude Haiku 4.5 (fast + reliable, ~3× cheaper than Sonnet)
#   @pro    — Gemini 2.5 Pro (cheaper still, weaker on tools)
#   @flash  — Gemini 2.5 Flash (cheapest, weakest on tools)
#   @lite   — Gemini 2.5 Flash Lite (extreme cheap)
MODEL_PREFIXES = {
    "@sonnet ": SONNET_MODEL,
    "@haiku ": HAIKU_MODEL,
    "@pro ": PRO_MODEL,
    "@flash ": FLASH_MODEL,
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


def _tool_write(artist_root: Path, args: dict) -> dict:
    path = _resolve_path(artist_root, args["file_path"])
    pre_text = ""
    is_new = not path.exists()
    if not is_new:
        try:
            pre_text = path.read_text(encoding="utf-8")
        except Exception:
            pre_text = ""
    path.parent.mkdir(parents=True, exist_ok=True)
    new_text = args["content"]
    path.write_text(new_text, encoding="utf-8")
    diff = "".join(difflib.unified_diff(
        pre_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=("(new) " + args["file_path"]) if is_new else args["file_path"],
        tofile=args["file_path"], n=2,
    ))
    added = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    label = "Created" if is_new else "Wrote"
    return {
        "text": f"{label} {args['file_path']} ({len(new_text)} bytes)",
        "meta": {"diff": diff, "path": args["file_path"], "tool": "Write",
                 "added": added, "removed": removed, "is_new": is_new},
    }


def _tool_edit(artist_root: Path, args: dict) -> dict:
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
    diff = "".join(difflib.unified_diff(
        text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=args["file_path"], tofile=args["file_path"], n=2,
    ))
    added = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    return {
        "text": f"Replaced {n} occurrence(s) in {args['file_path']}",
        "meta": {"diff": diff, "path": args["file_path"], "tool": "Edit",
                 "added": added, "removed": removed},
    }


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


# ── Hallucination guard ───────────────────────────────────────────────────────
# Catches the model claiming "I've edited X" without actually calling Edit.
# Triggers a corrective re-iteration in the same turn so the user just sees
# the work happen, not the model's apology.

_HALLUCINATION_PHRASES = (
    "i've edited", "i edited",
    "i've changed", "i changed",
    "i've updated", "i updated",
    "i've added", "i added",
    "i've removed", "i removed",
    "i've replaced", "i replaced",
    "i've fixed", "i fixed",
    "i've corrected", "i corrected",
    "i've modified", "i modified",
    "i've made the change", "i've made the changes",
    "i've now applied", "i've applied",
    "i've performed",
    "the file now", "the change has been", "changes have been applied",
    "the new version reads", "the new code reads",
    "the file has been", "the page has been",
)

_USER_CHANGE_INDICATORS = (
    "change", "edit", "add ", "remove", "fix", "update", "replace",
    "rebuild", "rewrite", "merge", "delete", "swap", "modify",
    "alter", "refactor", "adjust", "tweak",
    "make ", "make it ", "make the ",
    "set the ", "create ", "write ", "build ",
    "convert ", "move ", "rename ",
)


def _detect_hallucinated_edit(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(phrase in lower for phrase in _HALLUCINATION_PHRASES)


def _looks_like_change_request(prompt: str) -> bool:
    if not prompt:
        return False
    lower = prompt.lower()
    return any(ind in lower for ind in _USER_CHANGE_INDICATORS)


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
    # Always refresh the system prompt at history[0]. The docs/*.md files in
    # _shared/docs/ change occasionally; without this, an old session keeps
    # the stale prompt until the user runs /clear (which we don't want — they
    # shouldn't have to know that). Cheap: dropping/setting one message.
    if history and history[0].get("role") == "system":
        history[0]["content"] = system_prompt
    elif not history:
        history.append({"role": "system", "content": system_prompt})
    else:
        # Defensive: history exists but no system message at index 0. Insert.
        history.insert(0, {"role": "system", "content": system_prompt})
    history.append({"role": "user", "content": prompt})

    started = time.time()
    total_cost: float = 0.0
    final_text = ""

    total_tokens = 0  # rolling token usage for the cost-meter context bar

    try:
        for iteration in range(1, MAX_ITERATIONS + 1):
            # Stream the model's output. Text deltas go straight to the wire as
            # content_block_delta events (typewriter effect — dashboard parses at
            # line 6514). Tool calls accumulate across chunks and are emitted in
            # one assistant event after the stream finishes.
            try:
                response_stream = litellm.completion(
                    model=model,
                    messages=history,
                    tools=_tool_specs(),
                    tool_choice="auto",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    api_base="https://openrouter.ai/api/v1",
                    temperature=0.3,
                    stream=True,
                    stream_options={"include_usage": True},
                )
            except Exception as e:
                log.error(f"{slug_tag}LLM error iteration {iteration}: {e}")
                yield {"type": "error", "error": f"Model call failed: {e}"}
                return

            text = ""
            tool_calls_acc: list[dict] = []
            chunks: list = []

            try:
                for chunk in response_stream:
                    chunks.append(chunk)
                    if not getattr(chunk, "choices", None):
                        continue
                    delta = chunk.choices[0].delta
                    if delta is None:
                        continue
                    content_piece = getattr(delta, "content", None)
                    if content_piece:
                        text += content_piece
                        yield {
                            "type": "content_block_delta",
                            "delta": {"type": "text_delta", "text": content_piece},
                        }
                    for tc in (getattr(delta, "tool_calls", None) or []):
                        idx = getattr(tc, "index", 0) or 0
                        while len(tool_calls_acc) <= idx:
                            tool_calls_acc.append({"id": "", "name": "", "arguments": ""})
                        slot = tool_calls_acc[idx]
                        if getattr(tc, "id", None):
                            slot["id"] = tc.id
                        fn = getattr(tc, "function", None)
                        if fn:
                            if getattr(fn, "name", None):
                                slot["name"] += fn.name
                            if getattr(fn, "arguments", None):
                                slot["arguments"] += fn.arguments
            except Exception as e:
                log.exception(f"{slug_tag}stream error iteration {iteration}")
                yield {"type": "error", "error": f"Stream error: {e}"}
                return

            tool_calls_acc = [tc for tc in tool_calls_acc if tc["name"]]

            # Cost + token usage from the assembled stream
            try:
                built = litellm.stream_chunk_builder(chunks, messages=history)
                turn_cost = float(litellm.completion_cost(built) or 0.0)
                total_cost += turn_cost
                usage = getattr(built, "usage", None)
                if usage is not None:
                    tt = getattr(usage, "total_tokens", 0) or 0
                    if tt:
                        total_tokens = int(tt)
            except Exception:
                turn_cost = 0.0

            # Build content array (text + tool_use blocks)
            content_blocks: list[dict] = []
            if text:
                content_blocks.append({"type": "text", "text": text})
                final_text = text
            for tc in tool_calls_acc:
                try:
                    parsed_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    parsed_args = {"_raw": tc["arguments"]}
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": parsed_args,
                })
                snippet = json.dumps(parsed_args)[:300]
                log.info(f"{slug_tag}TOOL: {tc['name']} → {snippet}")

            yield {"type": "assistant", "message": {"content": content_blocks}}

            history.append({
                "role": "assistant",
                "content": text or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["arguments"]},
                    } for tc in tool_calls_acc
                ] if tool_calls_acc else None,
            })

            # No tool calls → maybe done. Hallucination guard fires if the
            # model claimed an edit in chat but didn't actually call a tool.
            if not tool_calls_acc:
                hallucinated = (
                    _looks_like_change_request(prompt)
                    and _detect_hallucinated_edit(text)
                    and iteration < MAX_ITERATIONS
                )
                if hallucinated:
                    log.warning(
                        f"{slug_tag}HALLUCINATION GUARD fired iteration={iteration}: "
                        f"text claims edit but no tool calls. Pushing back."
                    )
                    yield {
                        "type": "system_message",
                        "text": "Detected claimed edit with no tool call — pushing back.",
                    }
                    history.append({
                        "role": "user",
                        "content": (
                            "Stop. You said you made a change but called no tools "
                            "this turn. The file has not changed. Use the Edit "
                            "(or Write/Bash) tool now to actually make the change "
                            "the user asked for. Do NOT paste the new code in chat "
                            "as proof — execute the tool. After the tool call "
                            "succeeds, briefly confirm what you did."
                        ),
                    })
                    continue  # next iteration retries with the corrective nudge

                if text:
                    log.info(f"{slug_tag}TEXT: {text[:500]}")
                duration_ms = int((time.time() - started) * 1000)
                log.info(
                    f"{slug_tag}── END (ok) cost=${total_cost:.4f} "
                    f"tokens={total_tokens} duration={duration_ms}ms ──"
                )
                yield {
                    "type": "result",
                    "result": final_text,
                    "cost_usd": round(total_cost, 6),
                    "tokens": total_tokens,
                    "duration_ms": duration_ms,
                }
                return

            # Execute each tool call
            for tc in tool_calls_acc:
                name = tc["name"]
                try:
                    args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    args = {}

                impl = TOOL_IMPLS.get(name)
                result_meta: dict = {}
                if impl is None:
                    result_text = f"Unknown tool: {name}"
                    is_error = True
                else:
                    try:
                        raw = impl(artist_root, args)
                        if isinstance(raw, dict):
                            result_text = raw.get("text", "")
                            result_meta = raw.get("meta", {}) or {}
                        else:
                            result_text = raw
                        is_error = False
                    except (PermissionError, FileNotFoundError, IsADirectoryError, ValueError) as e:
                        result_text = f"{type(e).__name__}: {e}"
                        is_error = True
                    except subprocess.TimeoutExpired:
                        result_text = "Bash command timed out"
                        is_error = True
                    except Exception as e:
                        log.exception(f"{slug_tag}Tool {name} crashed")
                        result_text = f"Tool crashed: {type(e).__name__}: {e}"
                        is_error = True

                if len(result_text) > 30_000:
                    result_text = result_text[:30_000] + "\n... (truncated)"

                event: dict = {
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": result_text,
                    "is_error": is_error,
                }
                if result_meta:
                    event["meta"] = result_meta
                yield event

                history.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_text,
                })

        log.warning(f"{slug_tag}Reached MAX_ITERATIONS={MAX_ITERATIONS}")
        yield {
            "type": "error",
            "error": f"Reached the {MAX_ITERATIONS}-step safety limit. Try splitting the request.",
        }
    finally:
        save_history(sessions_dir, session_id, history)
