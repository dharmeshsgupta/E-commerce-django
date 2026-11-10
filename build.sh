#!/usr/bin/env bash
set -o errexit

export PIP_BREAK_SYSTEM_PACKAGES=1
export PYTHONUNBUFFERED=1

if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements.txt --system
else
    pip install -r requirements.txt
fi

python manage.py collectstatic --no-input --clear
