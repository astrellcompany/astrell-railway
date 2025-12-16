"""
Django settings for astrellcapitalinvest project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-key"  # fallback for local only
)

# DEBUG
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")


ALLOWED_HOSTS = [
    "astrellcapitalinvest-production.up.railway.app",
    "web-production-ee2d.up.railway.app",   # ADD THIS
    "astrellcompany.com",
    "www.astrellcompany.com",
    "localhost",
    "127.0.0.1",
]


CSRF_TRUSTED_ORIGINS = [
    "https://astrellcapitalinvest-production.up.railway.app",
    "https://web-production-ee2d.up.railway.app",  # ADD THIS
    "https://astrellcapitalinvest.com",
    "https://www.astrellcapitalinvest.com",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------
# APPLICATIONS
# ---------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your apps
    "home",
    "userprofile",
    "django_countries",
    "connectwallet",
    "investment",
    "widget_tweaks",
]

# ---------------------------------------
# MIDDLEWARE
# ---------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # MUST remain here
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "astrellcapitalinvest.urls"

# ---------------------------------------
# TEMPLATES
# ---------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "astrellcapitalinvest.wsgi.application"

# ---------------------------------------
# DATABASE — RAILWAY POSTGRES (AUTO)
# ---------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
    )
}

# ---------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------
# STATIC FILES (RAILWAY + WHITENOISE)
# ---------------------------------------
STATIC_URL = "/static/"

# Folder where Railway will collect static files
STATIC_ROOT = BASE_DIR / "staticfiles"

# Enable Whitenoise compressed static file storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Your project static folder
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# =========================
# MEDIA FILES (uploads)
# =========================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"




# ---------------------------------------
# LOGIN SETTINGS
# ---------------------------------------

LOGIN_URL = "/userprofile/login/"

# ---------------------------------------
# SECURITY SETTINGS
# ---------------------------------------

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ---------------------------------------
# EMAIL SETTINGS — RESEND (RECOMMENDED)
# ---------------------------------------


# Resend API Key
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Default sender email (Resend requires domain verification)
DEFAULT_FROM_EMAIL = "support@astrellcompany.com"
DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "support@astrellcompany.com")


# ---------------------------------------
# LOGGING
# ---------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
