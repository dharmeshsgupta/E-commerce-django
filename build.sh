#!/usr/bin/env bash
set -o errexit

if command -v uv >/dev/null 2>&1; then
    uv pip install --system -r requirements.txt
elif python3 -m venv /tmp/build_venv 2>/dev/null; then
    source /tmp/build_venv/bin/activate
    pip install -r requirements.txt
else
    python3 -m pip install --break-system-packages -r requirements.txt || pip install --break-system-packages -r requirements.txt
fi

python manage.py collectstatic --no-input --clear
