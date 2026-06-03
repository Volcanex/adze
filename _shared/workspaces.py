"""Workspace integration config.

Each workspace can have its own Slack workspace, Figma file, etc. The artist's
`workspace` field (on `config.json`) determines which integration set applies.
Drop a future workspace ('personal', a second client, etc.) in here with its
own env-sourced credentials — nothing else in the code needs to change.
"""

import os


WORKSPACES = {
    'lastplace': {
        'slack': {
            'token': os.environ.get('LASTPLACE_SLACK_TOKEN', ''),
            'workspace_url': os.environ.get('LASTPLACE_SLACK_URL', 'https://lastplaceworkspace.slack.com'),
            'channel_prefix': 'artist-',
            # Channel name (without #) the bot posts new-artist announcements
            # into. Bot must be a member: `/invite @Last Place` in that
            # channel once. Lets users click through and join per-artist
            # channels instead of needing auto-invite.
            'announce_channel': os.environ.get('LASTPLACE_SLACK_ANNOUNCE_CHANNEL', 'adze'),
        },
    },
    'personal': {
        # No integrations yet. Add a slack block here if you ever want
        # personal-workspace artists to get their own channels.
    },
}


def integration(workspace, name):
    """Return the integration config for (workspace, name), or None if the
    workspace has no such integration set up."""
    ws = WORKSPACES.get(workspace) or {}
    return ws.get(name)
