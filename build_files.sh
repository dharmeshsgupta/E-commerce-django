#!/bin/bash
set -e

echo "=== Vercel Build Step: Installing dependencies ==="

# 1. If uv is available, use uv pip install
if command -v uv >/dev/null 2>&1; then
    echo "Using uv to install dependencies..."
    uv pip install --system -r requirements.txt
# 2. Try creating a clean virtual environment (avoids PEP 668 completely)
elif python3 -m venv /tmp/build_venv 2>/dev/null; then
    echo "Created build virtualenv at /tmp/build_venv..."
    source /tmp/build_venv/bin/activate
    pip install -r requirements.txt
# 3. Fallback to pip with --break-system-packages
else
    echo "Falling back to pip with --break-system-packages..."
    python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt || pip install --break-system-packages --no-cache-dir -r requirements.txt
fi

echo "=== Vercel Build Step: Collecting static files ==="
python3 manage.py collectstatic --noinput --clear 2>/dev/null || python manage.py collectstatic --noinput --clear

echo "=== Vercel Build Step: Setting up static files directory structure ==="
mkdir -p staticfiles/static
cp -r staticfiles/admin staticfiles/css staticfiles/js staticfiles/images staticfiles/static/ 2>/dev/null || true

echo "=== Build finished successfully! ==="
