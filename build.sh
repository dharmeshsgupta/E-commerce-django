#!/usr/bin/env bash
set -o errexit

if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt --system
else
    python3 -m pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt --break-system-packages
fi

python manage.py collectstatic --no-input --clear
