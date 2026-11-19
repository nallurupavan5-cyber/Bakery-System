import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Helper to read .env file if python-dotenv is not present
def load_env_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip("'").strip('"')
                    if key not in os.environ:
                        os.environ[key] = val

load_env_file(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-bakery-secret-key-change-in-production')
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'bakery_db')
    
    if DATABASE_URL:
        # Normalize postgres/mysql URL prefixes if needed
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif os.environ.get('USE_MYSQL', '').lower() in ('1', 'true', 'yes'):
        pwd = f":{MYSQL_PASSWORD}" if MYSQL_PASSWORD else ""
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}{pwd}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
        )
    else:
        # SQLite by default for instant zero-dependency execution, seamlessly swappable to MySQL
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'bakery.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    } if 'mysql' in SQLALCHEMY_DATABASE_URI else {}

    # File Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # Session & Security
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Business Defaults
    BAKERY_NAME = os.environ.get('BAKERY_NAME', 'Sweet Delights Artisan Bakery')
    BAKERY_PHONE = os.environ.get('BAKERY_PHONE', '+1 (555) 234-5678')
    BAKERY_EMAIL = os.environ.get('BAKERY_EMAIL', 'contact@sweetdelightsbakery.com')
    BAKERY_ADDRESS = os.environ.get('BAKERY_ADDRESS', '124 Sugarloaf Lane, Flour District, Suite 100')
    CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '$')
    DEFAULT_TAX_PERCENT = float(os.environ.get('DEFAULT_TAX_PERCENT', 5.0))
    DEFAULT_DISCOUNT_PERCENT = float(os.environ.get('DEFAULT_DISCOUNT_PERCENT', 0.0))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'
