import os
from app import create_app

# WSGI entry point for Render/Gunicorn
application = create_app()
