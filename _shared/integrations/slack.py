"""Slack integration.

One channel per artist in the artist's workspace's Slack (if that workspace
has Slack configured in `_shared/workspaces.py`). A pinned message in each
channel links back to the Adze admin, the live site, and the Figma file.

Failures never block artist creation — every call is wrapped in try/except,
logged, and surfaced via the artist's `slack_status` field on config.json.
"""

import json
import logging
import os
from pathlib import Path

import requests

from workspaces import integration

log = logging.getLogger(__name__)

SLACK_API = 'https://slack.com/api'
ADMIN_BASE = os.environ.get('ADZE_ADMIN_BASE_URL', 'https://adze.studio')


def _read_cfg(slug):
    p = Path(f'artists/{slug}/config.json')
    if not p.exists():
        return None, None
    return p, json.loads(p.read_text())


def _write_cfg(path, cfg):
    path.write_text(json.dumps(cfg, indent=4) + '\n', encoding='utf-8')


def _slack_call(token, method, payload):
    """POST to the Slack Web API. Returns the parsed JSON (with `ok` flag),
    or {'ok': False, 'error': str(e)} on transport failure."""
    try:
        r = requests.post(
            f'{SLACK_API}/{method}',
            headers={'Authorization': f'Bearer {token}',
                     'Content-Type': 'application/json; charset=utf-8'},
            json=payload, timeout=10,
        )
        return r.json()
    except (requests.RequestException, ValueError) as e:
        return {'ok': False, 'error': f'transport: {e}'}


def _pinned_message_text(cfg):
    """Markdown for the canonical pinned message. Edited in place when
    fields change (domain goes live, Figma URL set, etc)."""
    name = cfg.get('name') or cfg.get('slug', '')
    slug = cfg.get('slug', '')
    domain = cfg.get('domain', '')
    # Intake URL is derived from the artist's stored intake_token — admin_api
    # only persists the token, not the full URL.
    intake_token = cfg.get('intake_token')
    intake = f'{ADMIN_BASE}/intake/{slug}/{intake_token}' if intake_token else cfg.get('intake_url', '')

    # Figma is intentionally NOT here — it gets its own pinned message so
    # the latest design link unfurls on its own (Slack only unfurls bare
    # URLs, not <url|text> link syntax).
    lines = [f'*{name}*']
    lines.append(f'<{ADMIN_BASE}/admin/artist/{slug}|Adze admin>')
    if domain:
        lines.append(f'<https://{domain}|Live site> — `{domain}`')
    else:
        lines.append('_No domain set yet._')
    if intake:
        lines.append(f'<{intake}|Intake portal>')
    return '\n'.join(lines)


def ensure_artist_channel(slug):
    """Create (or look up) the artist's Slack channel and pin the canonical
    info message. Idempotent — running it twice is a no-op the second time
    apart from refreshing the pinned message text.

    Returns a dict {ok, channel_id?, error?}.
    """
    cfg_path, cfg = _read_cfg(slug)
    if not cfg:
        return {'ok': False, 'error': 'artist not found'}

    workspace = (cfg.get('workspace') or 'lastplace').lower()
    slack_cfg = integration(workspace, 'slack')
    if not slack_cfg or not slack_cfg.get('token'):
        return {'ok': False, 'error': f'workspace {workspace!r} has no Slack configured'}

    token = slack_cfg['token']
    channel_name = f"{slack_cfg.get('channel_prefix', 'artist-')}{slug}"

    channel_id = cfg.get('slack_channel_id')

    # Create the channel if we don't have its ID yet.
    if not channel_id:
        res = _slack_call(token, 'conversations.create',
                          {'name': channel_name, 'is_private': False})
        if res.get('ok'):
            channel_id = res['channel']['id']
        elif res.get('error') == 'name_taken':
            # Channel already exists in Slack — look it up.
            channel_id = _find_channel_by_name(token, channel_name)
            if not channel_id:
                cfg['slack_status'] = f'lookup failed: {res.get("error")}'
                _write_cfg(cfg_path, cfg)
                return {'ok': False, 'error': res.get('error')}
        else:
            cfg['slack_status'] = f'create failed: {res.get("error")}'
            _write_cfg(cfg_path, cfg)
            return {'ok': False, 'error': res.get('error', 'unknown')}

    # Post + pin the canonical message. If we already have a pinned_ts,
    # update in place instead of re-pinning.
    text = _pinned_message_text(cfg)
    pinned_ts = cfg.get('slack_pinned_ts')

    if pinned_ts:
        _slack_call(token, 'chat.update',
                    {'channel': channel_id, 'ts': pinned_ts, 'text': text})
    else:
        post = _slack_call(token, 'chat.postMessage',
                           {'channel': channel_id, 'text': text, 'unfurl_links': True})
        if post.get('ok'):
            pinned_ts = post['ts']
            _slack_call(token, 'pins.add',
                        {'channel': channel_id, 'timestamp': pinned_ts})
        else:
            log.warning('slack post failed for %s: %s', slug, post.get('error'))

    # Announce in the workspace's general channel on first provision so
    # people can click through and join. Only fires once — `slack_announced`
    # flag prevents re-posting on refresh.
    if not cfg.get('slack_announced') and slack_cfg.get('announce_channel'):
        name = cfg.get('name') or slug
        admin_url = f'{ADMIN_BASE}/admin/artist/{slug}'
        announce_text = (f'New artist channel: <#{channel_id}> — *{name}*\n'
                         f'<{admin_url}|Open in Adze admin>')
        ann = _slack_call(token, 'chat.postMessage',
                          {'channel': slack_cfg['announce_channel'],
                           'text': announce_text, 'unfurl_links': False})
        if ann.get('ok'):
            cfg['slack_announced'] = True
        else:
            log.warning('slack announce failed for %s: %s', slug, ann.get('error'))

    # Persist channel + pin info on config.json.
    cfg['slack_channel_id'] = channel_id
    if pinned_ts:
        cfg['slack_pinned_ts'] = pinned_ts
    cfg.pop('slack_status', None)
    _write_cfg(cfg_path, cfg)
    return {'ok': True, 'channel_id': channel_id}


def _find_channel_by_name(token, name):
    """Page through conversations.list looking for `name`. Slack max 200/page."""
    cursor = ''
    while True:
        params = {'limit': 200, 'exclude_archived': True,
                  'types': 'public_channel,private_channel'}
        if cursor:
            params['cursor'] = cursor
        res = _slack_call(token, 'conversations.list', params)
        if not res.get('ok'):
            return None
        for ch in res.get('channels', []):
            if ch.get('name') == name:
                return ch['id']
        cursor = res.get('response_metadata', {}).get('next_cursor', '')
        if not cursor:
            return None


def post_to_artist_channel(slug, text):
    """Post a one-off message to an artist's channel (intake uploads, domain
    going live, etc). No-op if the artist has no provisioned channel."""
    _, cfg = _read_cfg(slug)
    if not cfg:
        return {'ok': False, 'error': 'artist not found'}
    channel_id = cfg.get('slack_channel_id')
    if not channel_id:
        return {'ok': False, 'error': 'no channel provisioned'}
    workspace = (cfg.get('workspace') or 'lastplace').lower()
    slack_cfg = integration(workspace, 'slack')
    if not slack_cfg or not slack_cfg.get('token'):
        return {'ok': False, 'error': 'no slack token'}
    return _slack_call(slack_cfg['token'], 'chat.postMessage',
                       {'channel': channel_id, 'text': text})


def refresh_pinned(slug):
    """Re-render the pinned message — call after editing domain/figma_url."""
    return ensure_artist_channel(slug)


# Bare-URL announcements per field. Slack only unfurls bare URLs (not
# <url|text> link syntax), so posting them as their own messages gets
# the Figma / site preview thumbnail and bumps the channel in the sidebar.
_FIELD_INTROS = {
    'figma_url': '🎨 Figma file added',
    'domain':    '🌐 Domain set',
}


def post_field_update(slug, field, value):
    """Post a bare-URL channel message when a tracked field changes. Returns
    silently if the artist has no provisioned channel or no Slack config.

    For `figma_url`: the message gets pinned, and the previous Figma-update
    pin (if any) is unpinned + deleted so the channel header always reflects
    the current Figma file."""
    if not value:
        return
    cfg_path, cfg = _read_cfg(slug)
    if not cfg:
        return
    channel_id = cfg.get('slack_channel_id')
    if not channel_id:
        return
    workspace = (cfg.get('workspace') or 'lastplace').lower()
    slack_cfg = integration(workspace, 'slack')
    if not slack_cfg or not slack_cfg.get('token'):
        return
    token = slack_cfg['token']
    intro = _FIELD_INTROS.get(field, f'{field} updated')
    if field == 'domain' and not value.startswith(('http://', 'https://')):
        value = f'https://{value}'
    text = f'{intro}\n{value}'
    res = _slack_call(token, 'chat.postMessage',
                      {'channel': channel_id, 'text': text, 'unfurl_links': True})

    if field == 'figma_url' and res.get('ok'):
        new_ts = res['ts']
        prev_ts = cfg.get('slack_figma_msg_ts')
        # Move the pin: unpin the previous Figma message but leave it in
        # the channel history. Only the latest is pinned; the history of
        # design links stays browsable in the channel scroll.
        if prev_ts:
            _slack_call(token, 'pins.remove',
                        {'channel': channel_id, 'timestamp': prev_ts})
        _slack_call(token, 'pins.add',
                    {'channel': channel_id, 'timestamp': new_ts})
        cfg['slack_figma_msg_ts'] = new_ts
        _write_cfg(cfg_path, cfg)
