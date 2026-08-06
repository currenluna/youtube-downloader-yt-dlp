#!/usr/bin/env bash
# One-command setup + launch: creates the venv if it's missing, keeps
# dependencies in sync with requirements.txt, then starts the server.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Creating virtual environment…"
  python3 -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt

echo "Starting server at http://localhost:5001"
exec .venv/bin/python app.py
