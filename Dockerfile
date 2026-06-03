FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    nodejs \
    npm \
    tmux \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI (same version as host)
RUN npm install -g @anthropic-ai/claude-code@2.0.37

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (artists/, output/, logs/ are mounted as volumes at runtime)
COPY . .

# Run as uid 1000 to match the per-artist sandbox container — otherwise
# Flask writes files as root that the sandbox (uid 1000) can't edit, and
# the user gets "permission denied" inside Auto-Code/Terminal Access.
# `adze` is in the `docker` group (host's docker.sock GID = 988) so Flask
# can still spawn sandbox containers via /var/run/docker.sock.
ARG DOCKER_GID=988
RUN groupadd -g ${DOCKER_GID} dockerhost \
 && useradd -u 1000 -m -s /bin/bash -G dockerhost adze \
 && chown -R adze:adze /app
USER adze

EXPOSE 5001

CMD ["python3", "flask_server.py", "--port", "5001", "--no-debug"]
