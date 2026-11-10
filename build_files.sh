#!/bin/bash
set -e

echo "=== Vercel Build Step: Setting up Python 3.12 environment ==="

if command -v uv >/dev/null 2>&1; then
    echo "Creating Python 3.12 virtualenv with uv..."
    uv venv --python 3.12 /tmp/build_venv
    source /tmp/build_venv/bin/activate
    echo "Installing dependencies with uv..."
    uv pip install -r requirements.txt
elif python3.12 -m venv /tmp/build_venv 2>/dev/null; then
    echo "Using python3.12 venv..."
    source /tmp/build_venv/bin/activate
    pip install -r requirements.txt
else
    echo "Using system venv..."
    python3 -m venv /tmp/build_venv || python -m venv /tmp/build_venv
    source /tmp/build_venv/bin/activate
    pip install -r requirements.txt
fi

echo "=== Vercel Build Step: Collecting static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Vercel Build Step: Setting up static and media files directory structure ==="
mkdir -p staticfiles/static
cp -r staticfiles/admin staticfiles/css staticfiles/js staticfiles/images staticfiles/static/ 2>/dev/null || true

# Copy media files to staticfiles/media for fast Vercel CDN serving
if [ -d "media" ]; then
    echo "Copying media uploads to staticfiles/media..."
    mkdir -p staticfiles/media
    cp -r media/* staticfiles/media/ 2>/dev/null || true
fi

echo "=== Build finished successfully! ==="
