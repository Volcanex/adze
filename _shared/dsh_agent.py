"""
Auto-Code agent backend — DeepSeek Harness driven through its Python SDK.

Replaces the `opencode serve`-inside-a-sandbox-container arrangement that
`autocode_proxy.py` used to reverse-proxy. The harness runtime is a
subprocess of *this* process now, spoken to over stdio JSON-RPC, so the
per-artist container, the minted HTTP Basic password, the readiness poll and
the orphan-reaper all stop being part of the picture.

Wire format is unchanged. `dashboard.html` speaks opencode's event schema and
knows nothing about DeepSeek, so `_translate()` maps harness notifications
onto that schema and the browser never learns the backend moved. That is the
whole reason this module is shaped the way it is: the alternative was editing
~1,200 lines of dashboard JS to learn a second event vocabulary.

Two things worth knowing before editing:

  * The model has **no shell**. `dsh_cordis.yml` deliberately omits the bash
    plugins, so file tools are the entire tool surface. If a prompt or doc
    tells the model to run a command, it cannot, and it will say so.

  * Sessions hold their peak RSS for as long as they live (~116MB for the
    first, ~55MB PSS for each additional one). Idle eviction is therefore
    load-bearing rather than an optimisation — see `IDLE_EVICT_SECONDS`.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
import time
from pathlib import Path
from typing import Any, Iterator

_log = logging.getLogger('adze.dsh')

try:
    from deepseek_harness import DeepSeekHarness, DeepSeekHarnessConfig
    _SDK_IMPORT_ERROR = None
except Exception as exc:                                  # pragma: no cover
    DeepSeekHarness = None                                # type: ignore
    DeepSeekHarnessConfig = None                          # type: ignore
    _SDK_IMPORT_ERROR = exc


CORDIS_CONFIG = Path(__file__).resolve().parent / 'dsh_cordis.yml'

# OpenRouter, so the existing OPENROUTER_API_KEY stays the only credential and
# `[tool.gcore].depends` needs no new entry. The provider id must stay
# "deepseek-official": that is the only LLM adapter mounted in dsh_cordis.yml,
# and the runtime rejects an unregistered provider name outright. It reaches
# OpenRouter through base_url, not through a different adapter.
PROVIDER = 'deepseek-official'
BASE_URL = os.environ.get('ADZE_DSH_BASE_URL', 'https://openrouter.ai/api/v1')

MODELS = {
    'flash': 'deepseek/deepseek-v4-flash',
    'pro': 'deepseek/deepseek-v4-pro',
}
# `pro` since 2026-08-25. Flash is not too dumb to write the code — its JS was
# fine — it is too loose to stay in its own directory. Same prompt, same artist,
# measured side by side: flash made 54 tool calls, ~30 of them on paths outside
# the artist it was working for, and rebuilt a different artist's site; pro made
# 16, all inside, and said plainly that the assets folder was empty instead of
# inventing "50+ images" to fill a gallery with. ~5x the price of flash, which
# is ~$0.003 for a typical page edit — far below the cost of one support email
# about a site that edited itself wrong.
#
# This is a tendency, not a boundary: pro would have been just as free to wander
# if it had decided to. The fence in dsh_cordis.yml is what makes it safe; this
# just makes it rarer.
DEFAULT_MODEL = MODELS['pro']

# USD per 1M tokens, used only to paint the dashboard's cost readout. These
# are DeepSeek's off-peak rates as of 2026-08-16; peak (01:00-04:00 and
# 06:00-10:00 UTC) is double, so treat the figure as a floor, not a bill.
PRICES = {
    'deepseek/deepseek-v4-flash': (0.22, 0.66),
    'deepseek/deepseek-v4-pro': (0.66, 1.98),
}

# Reported by the runtime as `contextWindow` on request/context. Only used to
# scale the dashboard's usage bar.
CONTEXT_WINDOW = 1_000_000

IDLE_EVICT_SECONDS = int(os.environ.get('ADZE_DSH_IDLE_EVICT', 15 * 60))
REQUEST_TIMEOUT_S = int(os.environ.get('ADZE_DSH_TIMEOUT', 600))

# Tools that mean "a file changed", so the turn should trigger a recompile:
# `dashboard.html` refreshes the preview and publishes on file.edited, and a
# turn that edits without emitting one leaves the artist's live site stale
# while the dashboard shows the new content. The names here are the tool
# names the model actually calls (`edit`, `write`, …) — NOT the plugin names
# in dsh_cordis.yml. `dsh-tool-str-replace-editor` registers a tool called
# `edit`; guessing from the plugin name is how this was wrong the first time.
_EDIT_TOOLS = {'edit', 'write', 'create', 'str_replace_editor', 'multi_edit', 'apply_patch'}


def sdk_available() -> tuple[bool, str]:
    if DeepSeekHarness is None:
        return False, f'deepseek-harness-sdk not importable: {_SDK_IMPORT_ERROR}'
    if not CORDIS_CONFIG.exists():
        return False, f'missing composition file {CORDIS_CONFIG}'
    return True, ''


# ── Event bus ────────────────────────────────────────────────────────────────
# One bus per artist. The SSE route subscribes; turns publish from whatever
# thread they run on. Subscribers that stop draining are dropped rather than
# allowed to pin a turn's memory — a dead EventSource must not be able to
# block the agent.

class _Bus:
    MAX_PENDING = 2000

    def __init__(self) -> None:
        self._subs: list[queue.Queue] = []
        self._lock = threading.Lock()

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=self.MAX_PENDING)
        with self._lock:
            self._subs.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._subs:
                self._subs.remove(q)

    def publish(self, event: dict) -> None:
        with self._lock:
            subs = list(self._subs)
        for q in subs:
            try:
                q.put_nowait(event)
            except queue.Full:
                _log.warning('dropping slow SSE subscriber')
                self.unsubscribe(q)


# ── Harness notification -> opencode event translation ───────────────────────

def _usage_to_tokens(usage: dict) -> dict:
    return {
        'input': usage.get('inputTokens', 0),
        'output': usage.get('outputTokens', 0),
        'reasoning': usage.get('reasoningTokens', 0),
        'cache': {'read': usage.get('cacheReadTokens', 0), 'write': 0},
    }


def _estimate_cost(model: str, usage: dict) -> float:
    inp, out = PRICES.get(model, (0.0, 0.0))
    return (usage.get('inputTokens', 0) * inp + usage.get('outputTokens', 0) * out) / 1_000_000


def _parse_args(raw: Any) -> Any:
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return raw
    return raw


def _tool_result_text(content: Any) -> str:
    """Flatten a tool-result content array into displayable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                out.append(block.get('text', ''))
            elif isinstance(block, dict):
                out.append(json.dumps(block)[:2000])
        return '\n'.join(out)
    return '' if content is None else json.dumps(content)[:4000]


class _TurnState:
    """Per-turn bookkeeping so parts can be addressed by stable ids.

    The harness identifies streamed content by (turn, step, block index) and
    tool activity by callId; the dashboard wants a flat partID per bubble.
    This holds the mapping for one turn.
    """

    def __init__(self, sid: str, model: str) -> None:
        self.sid = sid
        self.model = model
        self.message_id = f'msg-{int(time.time() * 1000)}'
        self.blocks: dict[tuple, str] = {}
        self.text: dict[str, str] = {}
        self.tools: dict[str, str] = {}
        # callId -> was this an edit tool? Keyed per call rather than a single
        # sticky flag, so a read that happens after an edit does not also
        # announce file.edited and trigger a redundant compile.
        self.tool_edits: dict[str, bool] = {}
        self.files_edited = False
        self.usage: dict = {}
        self.parts: list[dict] = []

    def text_part_id(self, text: str, fallback: str) -> str:
        """Id for a settled text that was already streamed as a block.

        The harness reports the final text three times — as deltas, in its
        assistant/message event, and in run()'s return value. The dashboard
        keys bubbles by part id, so the settled copies must reuse the
        streamed block's id or the same reply renders three times.
        """
        for pid, streamed in self.text.items():
            if pid.startswith('text-') and streamed == text:
                return pid
        return fallback

    def block_part_id(self, turn: Any, step: Any, index: Any, kind: str) -> str:
        key = (turn, step, index)
        if key not in self.blocks:
            self.blocks[key] = f'{kind}-{self.message_id}-{turn}-{step}-{index}'
        return self.blocks[key]


def _translate(payload: dict, st: _TurnState) -> list[dict]:
    """Map one harness notification payload onto zero or more opencode events."""
    sid = st.sid
    events: list[dict] = []
    ev = payload.get('event') or {}
    etype = ev.get('type')
    data = ev.get('data') or {}

    # session.status arrives as a bare payload, not wrapped in `event`.
    if 'status' in payload and not etype:
        status = payload.get('status')
        kind = 'busy' if status in ('running', 'busy') else 'idle'
        return [{'type': 'session.status',
                 'properties': {'sessionID': sid, 'status': {'type': kind}}}]

    if etype == 'turn/start':
        return [{'type': 'session.status',
                 'properties': {'sessionID': sid, 'status': {'type': 'busy'}}}]

    if etype == 'assistant/chunk':
        chunk = data.get('chunk') or {}
        ctype = chunk.get('type')
        index = chunk.get('index')
        turn, step = data.get('turn'), data.get('step')
        block_type = chunk.get('blockType')

        if ctype == 'block-start' and block_type in ('text', 'reasoning'):
            kind = 'reasoning' if block_type == 'reasoning' else 'text'
            pid = st.block_part_id(turn, step, index, kind)
            st.text.setdefault(pid, '')
            return [{'type': 'message.part.updated',
                     'properties': {'part': {'id': pid, 'sessionID': sid,
                                             'messageID': st.message_id,
                                             'type': kind, 'text': ''}}}]

        # Text deltas. The runtime has used several field names across rc
        # builds (`delta`, `text`, `textDelta`), so accept any of them rather
        # than pin to one and silently stream nothing when it is renamed.
        delta = chunk.get('delta')
        if delta is None:
            delta = chunk.get('text')
        if delta is None:
            delta = chunk.get('textDelta')
        if isinstance(delta, dict):
            delta = delta.get('text') or delta.get('value')
        if ctype in ('block-delta', 'delta', 'text-delta', 'block_delta') and isinstance(delta, str) and delta:
            key = (turn, step, index)
            pid = st.blocks.get(key) or st.block_part_id(turn, step, index, 'text')
            st.text[pid] = st.text.get(pid, '') + delta
            return [{'type': 'message.part.delta',
                     'properties': {'sessionID': sid, 'messageID': st.message_id,
                                    'partID': pid, 'field': 'text', 'delta': delta}}]
        return []

    if etype == 'tool/call':
        call_id = data.get('callId')
        name = data.get('name') or 'tool'
        pid = f'tool-{call_id}'
        st.tools[call_id] = pid
        is_edit = name in _EDIT_TOOLS
        st.tool_edits[call_id] = is_edit
        if is_edit:
            st.files_edited = True
        return [{'type': 'message.part.updated',
                 'properties': {'part': {'id': pid, 'sessionID': sid,
                                         'messageID': st.message_id,
                                         'type': 'tool', 'tool': name,
                                         'state': {'status': 'running',
                                                   'input': _parse_args(data.get('arguments'))}}}}]

    if etype == 'tool/result':
        message = data.get('message') or {}
        blocks = message.get('content') or []
        for block in blocks:
            if not isinstance(block, dict) or block.get('type') != 'tool-result':
                continue
            call_id = block.get('toolCallId')
            pid = st.tools.get(call_id, f'tool-{call_id}')
            is_error = bool(block.get('isError'))
            text = _tool_result_text(block.get('content'))
            state = ({'status': 'error', 'error': text} if is_error
                     else {'status': 'completed', 'output': text})
            events.append({'type': 'message.part.updated',
                           'properties': {'part': {'id': pid, 'sessionID': sid,
                                                   'messageID': st.message_id,
                                                   'type': 'tool', 'state': state}}})
            # Only announce a file change for a call that actually edited,
            # and only if it succeeded.
            if not is_error and st.tool_edits.get(call_id):
                events.append({'type': 'file.edited',
                               'properties': {'sessionID': sid, 'file': ''}})
        return events

    if etype == 'assistant/message':
        usage = ev.get('usage') or data.get('usage') or {}
        if usage:
            st.usage = usage
        message = data.get('message') or {}
        for block in message.get('content') or []:
            if isinstance(block, dict) and block.get('type') == 'text' and block.get('text'):
                pid = st.text_part_id(block['text'], f'final-{message.get("id", st.message_id)}')
                st.text[pid] = block['text']
                events.append({'type': 'message.part.updated',
                               'properties': {'part': {'id': pid, 'sessionID': sid,
                                                       'messageID': st.message_id,
                                                       'type': 'text', 'text': block['text']}}})
        if usage:
            events.append({'type': 'message.updated',
                           'properties': {'info': {'id': st.message_id, 'sessionID': sid,
                                                   'role': 'assistant',
                                                   'cost': _estimate_cost(st.model, usage),
                                                   'tokens': _usage_to_tokens(usage)}}})
        return events

    if etype == 'turn/end':
        reason = (data.get('reason') or {}).get('kind')
        if reason and reason != 'completed':
            events.append({'type': 'session.error',
                           'properties': {'sessionID': sid,
                                          'error': {'name': reason, 'message': f'turn ended: {reason}'}}})
        events.append({'type': 'session.idle', 'properties': {'sessionID': sid}})
        return events

    return []


# ── Sessions ─────────────────────────────────────────────────────────────────

class _Session:
    def __init__(self, slug: str, sid: str, workdir: Path, bus: _Bus, session_root: Path) -> None:
        self.slug = slug
        self.id = sid
        self.workdir = workdir
        self.bus = bus
        self.created_at = time.time()
        self.last_used = time.time()
        self.model = DEFAULT_MODEL
        self.title = ''
        self.history: list[dict] = []
        self._harness = None
        self._session_root = session_root
        self._lock = threading.Lock()
        self._abort = threading.Event()

    def _ensure_harness(self, model: str):
        if self._harness is not None and model == self.model:
            return self._harness
        if self._harness is not None:
            # Model switch: the runtime binds provider/model at initialize(),
            # so a change means a new runtime rather than a per-turn override.
            self.close()
        api_key = os.environ.get('OPENROUTER_API_KEY', '')
        if not api_key:
            raise RuntimeError('OPENROUTER_API_KEY is not set in the Adze environment')
        self.model = model
        self._harness = DeepSeekHarness(DeepSeekHarnessConfig(
            provider=PROVIDER,
            model=model,
            cwd=str(self.workdir),
            base_url=BASE_URL,
            api_key=api_key,
            cordis=str(CORDIS_CONFIG),
            session_root=str(self._session_root),
            request_timeout_seconds=REQUEST_TIMEOUT_S,
        ))
        self._harness.start()
        return self._harness

    def run(self, text: str, model: str | None = None) -> dict:
        """Run one turn. Blocks until the turn settles, streaming to the bus.

        The return value matches what the dashboard expects from opencode's
        POST /session/{id}/message: {'info': {...}, 'parts': [...]}.
        """
        with self._lock:
            self.last_used = time.time()
            self._abort.clear()
            st = _TurnState(self.id, model or self.model)
            h = self._ensure_harness(model or self.model)
            self.history.append({'role': 'user', 'text': text})

            def on_notification(n):
                try:
                    payload = getattr(n, 'payload', None) or {}
                    for event in _translate(payload, st):
                        self.bus.publish(event)
                except Exception:
                    _log.exception('[%s] translating harness notification failed', self.slug)

            try:
                result = h.run(text, on_notification=on_notification)
            except Exception as exc:
                _log.exception('[%s] turn failed', self.slug)
                self.bus.publish({'type': 'session.error',
                                  'properties': {'sessionID': self.id,
                                                 'error': {'name': type(exc).__name__,
                                                           'message': str(exc)}}})
                self.bus.publish({'type': 'session.idle', 'properties': {'sessionID': self.id}})
                return {'info': {'id': st.message_id, 'sessionID': self.id, 'role': 'assistant',
                                 'error': {'name': type(exc).__name__, 'message': str(exc)}},
                        'parts': []}

            self.last_used = time.time()
            final = result.final_response or ''
            if final:
                self.history.append({'role': 'assistant', 'text': final})
            if not self.title:
                self.title = (text[:60] + '…') if len(text) > 60 else text

            parts = [{'id': st.text_part_id(final, f'final-{st.message_id}'),
                      'type': 'text', 'text': final}] if final else []
            info = {'id': st.message_id, 'sessionID': self.id, 'role': 'assistant',
                    'cost': _estimate_cost(st.model, st.usage),
                    'tokens': _usage_to_tokens(st.usage)}
            return {'info': info, 'parts': parts, 'filesEdited': st.files_edited}

    def close(self) -> None:
        h, self._harness = self._harness, None
        if h is not None:
            try:
                h.close()
            except Exception:
                _log.warning('[%s] harness close failed', self.slug, exc_info=True)

    def summary(self) -> dict:
        return {'id': self.id, 'title': self.title,
                'time': {'created': int(self.created_at * 1000),
                         'updated': int(self.last_used * 1000)}}


class DshManager:
    """Owns every live agent session, keyed by artist slug."""

    def __init__(self) -> None:
        self._sessions: dict[str, _Session] = {}
        self._buses: dict[str, _Bus] = {}
        self._lock = threading.Lock()
        self._reaper = threading.Thread(target=self._evict_loop, daemon=True)
        self._reaper.start()

    def bus(self, slug: str) -> _Bus:
        with self._lock:
            if slug not in self._buses:
                self._buses[slug] = _Bus()
            return self._buses[slug]

    def create(self, slug: str, workdir: Path, session_root: Path) -> _Session:
        sid = f'ses-{slug}-{int(time.time() * 1000):x}'
        s = _Session(slug, sid, workdir, self.bus(slug), session_root)
        with self._lock:
            self._sessions[sid] = s
        return s

    def get(self, sid: str) -> _Session | None:
        with self._lock:
            return self._sessions.get(sid)

    def list_for(self, slug: str) -> list[dict]:
        with self._lock:
            return [s.summary() for s in self._sessions.values() if s.slug == slug]

    def delete(self, sid: str) -> bool:
        with self._lock:
            s = self._sessions.pop(sid, None)
        if s:
            s.close()
            return True
        return False

    def _evict_loop(self) -> None:
        while True:
            time.sleep(60)
            cutoff = time.time() - IDLE_EVICT_SECONDS
            with self._lock:
                stale = [s for s in self._sessions.values()
                         if s.last_used < cutoff and s._harness is not None]
            for s in stale:
                _log.info('[%s] evicting idle session %s', s.slug, s.id)
                # The session object survives eviction so the browser can keep
                # its id and resume; only the runtime subprocess is reclaimed,
                # and _ensure_harness respawns one on the next turn.
                s.close()


_mgr = DshManager()


def sse_stream(slug: str) -> Iterator[str]:
    """Yield opencode-shaped SSE frames for one artist."""
    bus = _mgr.bus(slug)
    q = bus.subscribe()
    try:
        yield f'data: {json.dumps({"type": "server.connected", "properties": {}})}\n\n'
        while True:
            try:
                event = q.get(timeout=20)
            except queue.Empty:
                yield f'data: {json.dumps({"type": "server.heartbeat", "properties": {}})}\n\n'
                continue
            yield f'data: {json.dumps(event)}\n\n'
    finally:
        bus.unsubscribe(q)
