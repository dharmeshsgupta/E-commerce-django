#!/bin/bash
set -e

echo "Installing dependencies..."
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt --system
else
    python3 -m pip install -r requirements.txt --break-system-packages 2>/dev/null || python -m pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt --break-system-packages
fi

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear 2>/dev/null || python manage.py collectstatic --noinput --clear

echo "Ensuring static assets directory compatibility..."
mkdir -p staticfiles/static
cp -r staticfiles/admin staticfiles/css staticfiles/js staticfiles/images staticfiles/static/ 2>/dev/null || true

echo "Build completed successfully!"
