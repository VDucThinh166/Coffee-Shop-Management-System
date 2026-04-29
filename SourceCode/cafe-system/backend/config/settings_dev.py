"""
Settings riêng cho việc tạo migrations (không cần MySQL).
Dùng SQLite để makemigrations/check model syntax mà không cần cài mysqlclient.
"""
from config.settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
    }
}

# Tắt debug toolbar khi chạy migrations
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [mw for mw in MIDDLEWARE if 'debug_toolbar' not in mw]
