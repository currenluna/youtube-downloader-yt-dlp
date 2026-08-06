#!/usr/bin/env bash
# Double-click in Finder to set up and launch (macOS runs .command files
# in Terminal automatically). Same logic as run.sh.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Creating virtual environment…"
  python3 -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt

echo "Starting server at http://localhost:5001"
.venv/bin/python app.py
