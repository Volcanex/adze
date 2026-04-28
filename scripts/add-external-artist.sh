#!/usr/bin/env bash
#
# Bootstrap an Adze "external artist" — one whose source files live on a
# remote Seed deployment reached over SSH.
#
# Usage:
#   scripts/add-external-artist.sh <slug> <ssh-host> <remote-path>
#
# Example:
#   scripts/add-external-artist.sh gabrielpenmancouk gabriel@example.com /home/gabriel/gabrielpenmancouk
#
# Creates:
#   artists/<slug>/
#     config.json          — skeleton with `remote` block
#     ssh_key, ssh_key.pub — fresh ed25519 keypair (mode 600 / 644)
#
# Then prints the pubkey and the smoke-test command to run after authorizing
# it on the Seed box.

set -euo pipefail

if [ $# -ne 3 ]; then
    cat >&2 <<EOF
usage: $0 <slug> <ssh-host> <remote-path>

  slug         e.g. "gabrielpenmancouk"
  ssh-host     e.g. "gabriel@example.com" or an ~/.ssh/config alias
  remote-path  absolute path to the Seed repo on the remote box
EOF
    exit 2
fi

SLUG="$1"
HOST="$2"
REMOTE_PATH="$3"

if [[ ! "$SLUG" =~ ^[a-z0-9_-]+$ ]]; then
    echo "error: slug must be [a-z0-9_-]+" >&2
    exit 2
fi

ARTIST_DIR="artists/$SLUG"
if [ -e "$ARTIST_DIR" ]; then
    echo "error: $ARTIST_DIR already exists; refusing to overwrite" >&2
    exit 1
fi

mkdir -p "$ARTIST_DIR"

# Domain is a placeholder — edit config.json after bootstrap if it differs
# from the Seed deployment's manifest.preview_url-derived host.
cat > "$ARTIST_DIR/config.json" <<EOF
{
  "name": "$SLUG",
  "slug": "$SLUG",
  "domain": "",
  "remote": {
    "host": "$HOST",
    "path": "$REMOTE_PATH",
    "key": "ssh_key"
  }
}
EOF

ssh-keygen -t ed25519 -N "" -C "adze-external:$SLUG" -f "$ARTIST_DIR/ssh_key" >/dev/null
chmod 600 "$ARTIST_DIR/ssh_key"
chmod 644 "$ARTIST_DIR/ssh_key.pub"

cat <<EOF

Created $ARTIST_DIR/

Next steps:

  1. Authorize the public key on the Seed box. Either:

       cat $ARTIST_DIR/ssh_key.pub | ssh $HOST 'cat >> ~/.ssh/authorized_keys'

     or paste this line into ~/.ssh/authorized_keys on the remote:

EOF

cat "$ARTIST_DIR/ssh_key.pub"

cat <<EOF

  2. Smoke-test the connection:

       ssh -i $ARTIST_DIR/ssh_key -o BatchMode=yes -o StrictHostKeyChecking=accept-new \\
           $HOST "cd $REMOTE_PATH && pwd && ls -1 | head"

  3. (Optional) Drop a .adze-remote.json at the Seed repo root to override
     defaults (preview_url, build_command, client_brief).

  4. Restart adze-flask so the new artist is picked up:

       docker restart adze-flask

EOF
