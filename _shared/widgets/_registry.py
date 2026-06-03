"""Widget / tab registry.

Two-tier model:
  t1 — global; everyone sees it.
  t2 — workspace-scoped; only visible to identities whose workspaces include
       the widget's `workspace` field. When the viewer can see more than one
       workspace (e.g. Gabriel), t2 labels get prefixed with the workspace
       name: "LastPlace Slack". For single-workspace viewers (e.g. Clive)
       the prefix is dropped — context is already implicit.

A widget is registered by dropping a `manifest.json` in its folder:

    {
      "slug": "slack",
      "label": "Slack",
      "tier": "t2",
      "workspace": "lastplace"
    }

Tabs that already live in admin.html can be registered the same way via
TABS below — they aren't loaded from disk, they're declared inline.
"""

import json
from pathlib import Path


WORKSPACE_NAMES = {
    'lastplace': 'LastPlace',
    'personal':  'Personal',
}


# Tabs hard-coded in admin.html. Listed here so the workspace gate is
# applied uniformly and the front-end can ask the server which tabs to
# render. Order matters: it's the render order.
import os

# An external link-tab carries an `href` — clicking opens the URL in a new
# tab rather than switching to a panel. Used for tools we don't host
# (Slack, Figma, etc).
TABS = [
    {'slug': 'overview', 'label': 'Overview', 'tier': 't1'},
    {'slug': 'artists',  'label': 'Artists',  'tier': 't1'},
    {'slug': 'leads',    'label': 'Leads',    'tier': 't1'},
    {'slug': 'todos',    'label': 'To-dos',   'tier': 't1'},
    {'slug': 'hours',    'label': 'Hours',    'tier': 't2', 'workspace': 'lastplace'},
    {
        'slug': 'slack', 'label': 'Slack', 'tier': 't2', 'workspace': 'lastplace',
        'href': os.environ.get('LASTPLACE_SLACK_URL', 'https://lastplaceworkspace.slack.com'),
        'external': True,
    },
    {'slug': 'extras', 'label': 'Extras', 'tier': 't1'},
]


def _load_widget_manifests():
    """Walk _shared/widgets/*/manifest.json and return their dicts."""
    widgets_dir = Path(__file__).parent
    manifests = []
    for item in sorted(widgets_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('_'):
            continue
        mf = item / 'manifest.json'
        if not mf.exists():
            continue
        try:
            data = json.loads(mf.read_text())
            data.setdefault('slug', item.name)
            manifests.append(data)
        except (json.JSONDecodeError, IOError):
            continue
    return manifests


def _visible(entry, workspaces):
    """True if `entry` is visible to an identity holding `workspaces`."""
    if entry.get('tier', 't1') == 't1':
        return True
    return entry.get('workspace') in workspaces


def _display_label(entry, workspaces):
    """Apply the prefix rule: t2 widgets get a workspace prefix when the
    viewer can see more than one workspace."""
    label = entry.get('label') or entry.get('slug', '')
    if entry.get('tier') == 't2' and len(workspaces) > 1:
        ws = entry.get('workspace', '')
        prefix = WORKSPACE_NAMES.get(ws, ws.title())
        return f'{prefix} {label}'
    return label


def visible_tabs(workspaces):
    """Tabs the given identity should see, with labels resolved."""
    out = []
    for t in TABS:
        if not _visible(t, workspaces):
            continue
        out.append({**t, 'label': _display_label(t, workspaces)})
    return out


def visible_widgets(workspaces):
    """Widget manifests the given identity should see, with labels resolved.
    Widgets live under the Integrations tab."""
    out = []
    for w in _load_widget_manifests():
        if not _visible(w, workspaces):
            continue
        out.append({**w, 'label': _display_label(w, workspaces)})
    return out
