"""
Vercel WSGI Application Entry Point with Static Files Support
"""

import os
import sys
from pathlib import Path

# Add the project directory to the sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Import Django and setup
import django

django.setup()

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Get the base WSGI application
django_app = get_wsgi_application()

# Wrap with WhiteNoise for static files serving
from whitenoise import WhiteNoise

application = WhiteNoise(django_app, root=os.path.join(BASE_DIR, "staticfiles"))

# Add static files with proper MIME types for PWA
application.add_files(os.path.join(BASE_DIR, "staticfiles"), prefix="static/")

# Vercel handler
app = application
