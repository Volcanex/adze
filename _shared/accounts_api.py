"""
Account routes — /api/adze/account/*

Sign-in, sign-out, identifier resolution and password reset. A separate
blueprint rather than more lines in admin_api.py, which is already 7000+.

Reset only ever goes to a *verified* email. An artist who typo'd their address
would otherwise have every future reset silently swallowed, and the whole point
of this system is that Gabriel stops being the reset mechanism.
"""

import os

from flask import Blueprint, jsonify, make_response, redirect, request

import accounts

bp = Blueprint('accounts_api', __name__, url_prefix='/api/adze/account')

RESET_PATH = '/api/adze/account/reset/'


def _base_url():
    return (os.environ.get('ADZE_ADMIN_BASE_URL') or 'https://adze.studio').rstrip('/')


def _rate(scope, n, window):
    try:
        from admin_api import _rate_limit
        _rate_limit(scope, n, window)
    except ImportError:
        pass


def _client_ip():
    return request.headers.get('X-Real-IP') or request.remote_addr or ''


def _set_session_cookie(resp, slug, sid):
    resp.set_cookie('adze_session', f'{slug}:{sid}', httponly=True, samesite='Lax',
                    secure=request.headers.get('X-Forwarded-Proto') == 'https',
                    max_age=30 * 24 * 3600, path='/')
    return resp


@bp.route('/resolve', methods=['POST'])
def resolve():
    """Identifier -> where to send them. The adze.studio sign-in asks for a name
    or email first, then either redirects to the artist's own domain or takes
    the password here.

    Only the identifier travels in that redirect, never a credential: a cookie
    minted on adze.studio could not be sent to ninasere.com anyway.
    """
    _rate('resolve', 20, 60)
    ident = ((request.get_json(silent=True) or {}).get('identifier') or '').strip()
    acct = accounts.resolve(ident)
    if not acct:
        # The roster is public on adze.studio, so this leaks nothing new --
        # but it isn't free to scrape either, hence the rate limit above.
        return jsonify({'found': False}), 404
    sites = accounts.sites_for(acct['id'])
    out = {'found': True, 'name': acct['display_name'], 'sites': sites}
    if len(sites) == 1:
        cfg = _artist_cfg(sites[0])
        domain = (cfg.get('domain') or '').replace('https://', '').replace('http://', '').strip('/')
        if domain:
            out['redirect'] = f'https://{domain}/admin'
    return jsonify(out)


def _artist_cfg(slug):
    import json
    from pathlib import Path
    try:
        return json.loads((Path('artists') / slug / 'config.json').read_text())
    except Exception:
        return {}


@bp.route('/login', methods=['POST'])
def login():
    """Complete a sign-in on adze.studio itself. Needed because only 5 artists
    have a live vhost — most have no domain to be redirected to."""
    _rate('acctlogin', 10, 60)
    data = request.get_json(silent=True) or {}
    ident = (data.get('identifier') or '').strip()
    password = data.get('password') or ''
    slug = (data.get('slug') or '').strip()

    acct = accounts.resolve(ident)
    if not acct or not accounts.verify_password(acct, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    _rate(f'acctlogin:{acct["id"]}', 5, 300)

    sites = accounts.sites_for(acct['id'])
    if not slug:
        if len(sites) == 1:
            slug = sites[0]
        elif len(sites) > 1:
            return jsonify({'ok': False, 'choose': True, 'sites': sites}), 200
        elif not acct['is_owner']:
            return jsonify({'error': 'That account has no sites'}), 403
    elif slug not in sites and not acct['is_owner']:
        return jsonify({'error': 'Invalid credentials'}), 401

    sid = accounts.create_session(acct['id'], slug, ip=_client_ip(),
                                  ua=request.headers.get('User-Agent'))
    accounts.record_login(acct['id'], _client_ip())
    resp = make_response(jsonify({'ok': True, 'slug': slug, 'name': acct['display_name']}))
    return _set_session_cookie(resp, slug, sid)


@bp.route('/logout', methods=['POST'])
def logout():
    cookie = request.cookies.get('adze_session', '')
    _, _, sid = cookie.partition(':')
    if sid.startswith(accounts.SESSION_PREFIX):
        accounts.revoke_session(sid)
    resp = make_response(jsonify({'ok': True}))
    resp.delete_cookie('adze_session', path='/')
    return resp


@bp.route('/forgot', methods=['POST'])
def forgot():
    """Always the same answer, always immediately.

    A different response for a known vs unknown account turns this into an
    account-enumeration oracle, and a synchronous send turns response *time*
    into the same oracle -- which is why mailer.send_async is used.
    """
    _rate('forgot', 5, 3600)
    ident = ((request.get_json(silent=True) or {}).get('identifier') or '').strip()
    generic = {'ok': True, 'message': (
        'If that account has a confirmed email address, a reset link is on its way. '
        'It can take a few minutes — and do check your spam folder.')}

    acct = accounts.resolve(ident)
    if not acct or not acct['email'] or not acct['email_verified']:
        return jsonify(generic)
    _rate(f'forgot:{acct["id"]}', 3, 3600)

    token = accounts.create_reset(acct['id'], ip=_client_ip())
    link = f'{_base_url()}{RESET_PATH}{token}'
    try:
        import mailer
        mailer.send_async(
            to=acct['email'],
            subject='Reset your Adze password',
            text_body=(
                f'Hello {acct["display_name"] or ""},\n\n'
                f'Someone asked to reset the password for your site. If that was '
                f'you, open this link within the hour:\n\n{link}\n\n'
                f'If it wasn\'t you, ignore this — your password has not changed.\n\n'
                f'{mailer.SPAM_WARNING}\n'))
    except Exception:
        pass
    return jsonify(generic)


@bp.route('/reset/<token>', methods=['GET'])
def reset_form(token):
    return make_response(_RESET_HTML.replace('{{TOKEN}}', token), 200,
                         {'Content-Type': 'text/html; charset=utf-8'})


@bp.route('/reset/<token>', methods=['POST'])
def reset_submit(token):
    _rate('reset', 10, 600)
    new = ((request.get_json(silent=True) or {}).get('password') or '').strip()
    if len(new) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    account_id = accounts.consume_reset(token)
    if not account_id:
        return jsonify({'error': 'That link has expired or was already used.'}), 400

    accounts.set_password(account_id, new)
    # The editor still authenticates with admin_token from config.json, so a
    # reset that only writes the hash would leave the artist's API key on the
    # old value. Same dual-write as the self-service change.
    for slug in accounts.sites_for(account_id):
        _sync_legacy_token(slug, new)
    accounts.revoke_all_for_account(account_id)
    return jsonify({'ok': True})


def _sync_legacy_token(slug, new_password):
    import json
    from pathlib import Path
    p = Path('artists') / slug / 'config.json'
    try:
        cfg = json.loads(p.read_text())
        cfg['admin_token'] = new_password
        p.write_text(json.dumps(cfg, indent=4) + '\n')
    except (OSError, json.JSONDecodeError):
        pass


_RESET_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Set a new password</title>
<style>
 body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
   background:#fbfbfd;color:#0b0d1a;display:flex;min-height:100vh;
   align-items:center;justify-content:center;margin:0}
 .box{width:100%;max-width:340px;padding:32px}
 h1{font-size:20px;margin:0 0 20px}
 input{width:100%;box-sizing:border-box;padding:10px 12px;font-size:14px;
   border:1px solid #d8d8e0;border-radius:8px;margin-bottom:12px}
 button{width:100%;padding:10px;font-size:14px;background:#1c4f82;color:#fff;
   border:0;border-radius:8px;cursor:pointer}
 .msg{margin-top:12px;font-size:13px;color:#6b6b76}
 .err{color:#b3261e}
</style></head><body><div class="box">
<h1>Set a new password</h1>
<input id="pw" type="password" placeholder="New password" autocomplete="new-password">
<input id="pw2" type="password" placeholder="Repeat it" autocomplete="new-password">
<button id="go">Save</button>
<div class="msg" id="msg"></div>
<script>
const t="{{TOKEN}}",m=document.getElementById('msg');
document.getElementById('go').onclick=async()=>{
  const a=document.getElementById('pw').value,b=document.getElementById('pw2').value;
  m.className='msg';
  if(a!==b){m.className='msg err';m.textContent='Those two don\\u2019t match.';return}
  const r=await fetch(location.pathname,{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify({password:a})});
  const j=await r.json().catch(()=>({}));
  if(r.ok){m.textContent='Saved. You can sign in with your new password now.';}
  else{m.className='msg err';m.textContent=j.error||'That didn\\u2019t work.';}
};
</script></div></body></html>
"""
