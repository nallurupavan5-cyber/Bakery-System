# extensions.py
"""Flask extensions used throughout the Sweet Delights Bakery app.
This file is imported by app.py to initialise the database, migrations,
and login manager.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialise extension objects – they will be bound to the Flask app in app.create_app()

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()
# Redirect unauthenticated users to the login view (adjust if your route name differs)
login_manager.login_view = "auth.login"
