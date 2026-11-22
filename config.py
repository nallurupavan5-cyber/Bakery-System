
import os
from urllib.parse import urlparse, urlunparse


class Config:
    # Flask secret key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-me"
    )

    # Database configuration
    _raw_db_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///bakery.db"
    )

    # Normalize PostgreSQL URL for SQLAlchemy
    if _raw_db_url.startswith("postgres://"):
        parsed = urlparse(_raw_db_url)
        _raw_db_url = urlunparse(
            ("postgresql",) + parsed[1:]
        )

    SQLALCHEMY_DATABASE_URI = _raw_db_url

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
