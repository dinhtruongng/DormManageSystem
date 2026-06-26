"""Django settings for the Student Dormitory Management System demo.

Environment-driven configuration. Defaults to a local SQLite database so the
demo runs with zero external services; set DATABASE_URL to a PostgreSQL
connection string for the report's target deployment.
"""

from pathlib import Path

from dotenv import load_dotenv
import os

# Determine environment variables from a local .env file when present.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-demo-only-key-replace-for-deployment-2026",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

# Hosts the app may serve. Local dev = ["*"]; production must be explicit
# (comma-separated DJANGO_ALLOWED_HOSTS, e.g. "yourname.pythonanywhere.com,localhost").
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()
]

# Same-origin POST forms are covered by CSRF_TRUSTED_ORIGINS below; for the demo
# the login form posts same-origin, so an empty default is fine.
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# Production hardening flags (honored when DEBUG=false). Safe to leave set;
# they are inert locally because DEBUG=True.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps, layered per the report's app layout (Section 6.3).
    "dorm_system.common",
    "dorm_system.accounts",
    "dorm_system.residents",
    "dorm_system.rooms",
    "dorm_system.assignments",
    "dorm_system.billing",
    "dorm_system.payments",
    "dorm_system.communications",
    "dorm_system.reports",
    "dorm_system.demo_data",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dorm_system.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "dorm_system" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dorm_system.accounts.context_processors.role_context",
            ],
        },
    },
]

WSGI_APPLICATION = "dorm_system.config.wsgi.application"


# Database: PostgreSQL per the report; SQLite fallback for local demo.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    # Minimal parser so we avoid adding dj-database-url as a dependency.
    from urllib.parse import urlparse

    _p = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _p.path.lstrip("/"),
            "USER": _p.username or "",
            "PASSWORD": _p.password or "",
            "HOST": _p.hostname or "",
            "PORT": str(_p.port) if _p.port else "",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Asia/Ho_Chi_Minh")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "dorm_system" / "static"]
# WhiteNoise: serve hashed, compressed static straight from STATIC_ROOT. Works
# locally and on hosts (PythonAnywhere) that don't serve Django static by default.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email backend: console in dev so payment-review digests are visible in logs.
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "25"))

# Role names used by the accounts app and permission checks.
ROLES = {
    "ADMIN": "Admin",
    "FINANCE": "Finance",
    "STUDENT": "Student",
    "SYSADMIN": "System Admin",
}

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"
