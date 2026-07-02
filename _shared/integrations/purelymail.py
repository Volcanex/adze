"""Purelymail integration (api/v0).

One Purelymail account hosts mail for every workspace domain; the
account-level token (see `_shared/workspaces.py` -> workspace 'email')
manages mailboxes and forwarding rules across all of them. Each call is a
POST with the token in the `Purelymail-Api-Token` header.

Scoping to a single artist's domain happens here: `list_domain_email`
filters the account-wide user/rule lists down to one domain so the
dashboard only ever shows (and touches) that site's addresses.

API reference: https://news.purelymail.com/api/index.html
"""

import json
import urllib.error
import urllib.request

BASE = 'https://purelymail.com/api/v0'


def _call(token, op, body):
    req = urllib.request.Request(
        f'{BASE}/{op}',
        data=json.dumps(body).encode(),
        headers={'Purelymail-Api-Token': token,
                 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {'type': 'error', 'code': e.code,
                    'message': e.read().decode()[:300]}


def ok(resp):
    return isinstance(resp, dict) and resp.get('type') == 'success'


def error_message(resp):
    return (resp or {}).get('message') or 'Purelymail API error'


def list_domain_email(token, domain):
    """Return (mailboxes, forwards) for one domain.

    mailboxes: [{'address': 'gabe@domain'}]
    forwards:  [{'id', 'address': 'support@domain', 'targets': [...], 'prefix'}]
    """
    suffix = '@' + domain
    users = _call(token, 'listUser', {}).get('result', {}).get('users', [])
    mailboxes = [{'address': u} for u in users if u.endswith(suffix)]

    rules = _call(token, 'listRoutingRules', {}).get('result', {}).get('rules', [])
    forwards = [{
        'id': r['id'],
        'address': f'{r["matchUser"]}@{r["domainName"]}',
        'targets': r.get('targetAddresses', []),
        'prefix': r.get('prefix', False),
    } for r in rules if r.get('domainName') == domain]

    return mailboxes, forwards


def create_mailbox(token, localpart, domain, password):
    return _call(token, 'createUser', {
        'userName': localpart,
        'domainName': domain,
        'password': password,
        'sendWelcomeEmail': False,
        'enableSearchIndexing': True,
    })


def delete_mailbox(token, address):
    return _call(token, 'deleteUser', {'userName': address})


def create_forward(token, localpart, domain, targets):
    return _call(token, 'createRoutingRule', {
        'domainName': domain,
        'prefix': False,
        'matchUser': localpart,
        'targetAddresses': targets,
        'catchall': False,
    })


def delete_forward(token, rule_id):
    return _call(token, 'deleteRoutingRule', {'routingRuleId': int(rule_id)})
