#!/bin/bash
set -e

export PIP_BREAK_SYSTEM_PACKAGES=1
export PYTHONUNBUFFERED=1

echo "Installing dependencies..."
if command -v uv >/dev/null 2>&1; then
    echo "Using uv to install dependencies..."
    uv pip install -r requirements.txt --system
elif command -v python3 >/dev/null 2>&1; then
    echo "Using python3 pip to install dependencies..."
    python3 -m pip install -r requirements.txt
else
    echo "Using pip to install dependencies..."
    pip install -r requirements.txt
fi

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear || python manage.py collectstatic --noinput --clear

echo "Ensuring static assets directory compatibility..."
mkdir -p staticfiles/static
cp -r staticfiles/admin staticfiles/css staticfiles/js staticfiles/images staticfiles/static/ 2>/dev/null || true

echo "Build completed successfully!"
