#!/bin/bash
# Vercel build script for SafeSite

echo "🔨 Running Django collectstatic..."
python manage.py collectstatic --noinput

echo "✅ Build complete!"
