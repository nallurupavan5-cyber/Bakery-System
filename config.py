
import os
from urllib.parse import urlparse, urlunparse


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-me"
    )

    _raw_db_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///bakery.db"
    )

    # Convert Render PostgreSQL URL to psycopg2 driver
    if _raw_db_url.startswith("postgres://"):
        parsed = urlparse(_raw_db_url)
        _raw_db_url = urlunparse(
            ("postgresql+psycopg2",) + parsed[1:]
        )

    elif _raw_db_url.startswith("postgresql://"):
        parsed = urlparse(_raw_db_url)
        _raw_db_url = urlunparse(
            ("postgresql+psycopg2",) + parsed[1:]
        )

    SQLALCHEMY_DATABASE_URI = _raw_db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
