import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from models.settings import SystemSetting


def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_uploaded_file(file_storage, subfolder=''):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Invalid file extension. Allowed: PNG, JPG, JPEG, WEBP, GIF.")

    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(target_dir, exist_ok=True)

    orig_name = secure_filename(file_storage.filename)
    ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'jpg'
    unique_name = f"{uuid.uuid4().hex[:12]}_{orig_name}"
    filepath = os.path.join(target_dir, unique_name)
    file_storage.save(filepath)

    return os.path.join(subfolder, unique_name).replace('\\', '/')


def format_currency(val):
    symbol = SystemSetting.get_value('currency_symbol', '$')
    try:
        num = float(val or 0.0)
        return f"{symbol}{num:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"
