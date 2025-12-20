#!/bin/bash

echo "Starting Vercel build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Debug: Check if PWA files were collected
echo "Verifying PWA files..."
if [ -f "staticfiles/pwa/manifest.json" ]; then
    echo "✓ manifest.json found"
    ls -lh staticfiles/pwa/manifest.json
else
    echo "✗ manifest.json NOT found"
fi

if [ -f "staticfiles/pwa/sw.js" ]; then
    echo "✓ sw.js found"
    ls -lh staticfiles/pwa/sw.js
else
    echo "✗ sw.js NOT found"
fi

echo "Total PWA files collected:"
ls -la staticfiles/pwa/ || echo "PWA directory not found!"

# Copy static files to public directory for Vercel to serve
echo "Copying static files to public directory..."
mkdir -p public
cp -r staticfiles/* public/ || echo "Failed to copy static files"
echo "Static files copied to public/"
ls -la public/pwa/ || echo "PWA files not in public directory"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build process completed successfully!"
