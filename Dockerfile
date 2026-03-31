FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI (same version as host)
RUN npm install -g @anthropic-ai/claude-code@2.0.37

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (artists/, output/, logs/ are mounted as volumes at runtime)
COPY . .

EXPOSE 5001

CMD ["python3", "flask_server.py", "--port", "5001", "--no-debug"]
