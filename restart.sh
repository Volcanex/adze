#!/bin/bash
# Restart Adze Studio Flask server cleanly
cd "$(dirname "$0")"

# Kill any existing processes on port 5001
lsof -i :5001 -t 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1

# Double check nothing is left
if lsof -i :5001 -t >/dev/null 2>&1; then
    echo "ERROR: Port 5001 still in use"
    exit 1
fi

# Start fresh
source venv/bin/activate
nohup python3 flask_server.py --port 5001 --no-debug > logs/flask_server.log 2>&1 &
echo $! > flask_server.pid
sleep 2

if curl -s -o /dev/null -w "" --max-time 5 http://localhost:5001/api/health; then
    echo "Adze Studio running on port 5001 (PID: $(cat flask_server.pid))"
else
    echo "ERROR: Server failed to start. Check logs/flask_server.log"
    exit 1
fi
