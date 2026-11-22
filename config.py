import os
from urllib.parse import urlparse, urlunparse


class Config:
    # Secret key – Render generates a secure value; fallback is safe for local dev
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Normalise DATABASE_URL – Render may supply a ``postgres://`` URL, but
    # SQLAlchemy (v2) expects the ``postgresql://`` scheme.
    _raw_db_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///bakery.db"
    )
    if _raw_db_url.startswith("postgres://"):
        # Replace only the scheme, keeping the rest of the URL intact.
        parsed = urlparse(_raw_db_url)
        _raw_db_url = urlunparse(("postgresql",) + parsed[1:])

    SQLALCHEMY_DATABASE_URI = _raw_db_url

    # Recommended defaults – disable unnecessary signalling overhead.
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///bakery.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
