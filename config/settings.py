"""
Django settings for WebJin (config project).

Secrets and environment-specific values come ONLY from the environment
(or a local .env loaded by python-dotenv). Never commit real keys or DB passwords.
"""

import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core security & host config (required)
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY is not set. "
        "Copy .env.example to .env and generate a key, e.g.: "
        "python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    )

# DEBUG must be an explicit env flag. Default False for safety on host.
DEBUG = os.environ.get('DEBUG', 'False').strip().lower() in ('1', 'true', 'yes', 'on')

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        '127.0.0.1,localhost',
    ).split(',')
    if h.strip()
]

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'csp',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django_cleanup',
    'captcha',
    'django_check_seo',
    'crispy_forms',
    'crispy_bootstrap5',
    # 'django_ratelimit',  # enable when CACHES is configured
    'admin_persian',
    'directory',
    'contact',
    'farsi',
    'taggit',
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # once only — early for static
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
SITE_ID = 1

# ---------------------------------------------------------------------------
# Database — SQLite in DEBUG, MySQL in production
# ---------------------------------------------------------------------------

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'dirwebir_direct'),
            'USER': os.environ.get('MYSQL_USER', ''),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ.get('MYSQL_HOST', '127.0.0.1'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'connect_timeout': 20,
                'read_timeout': 30,
                'write_timeout': 30,
            },
            'CONN_MAX_AGE': 60,
        }
    }
    # Fail fast if production credentials are missing
    if not DATABASES['default']['USER'] or not DATABASES['default']['PASSWORD']:
        raise ValueError(
            "MYSQL_USER and MYSQL_PASSWORD must be set when DEBUG=False"
        )

# ---------------------------------------------------------------------------
# Security headers (tighten automatically when not DEBUG)
# ---------------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Behind a reverse proxy / Passenger that terminates TLS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG

SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# CSRF trusted origins for production hosts (HTTPS)
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://webjin.ir,https://www.webjin.ir,https://dirweb.ir,https://www.dirweb.ir',
    ).split(',')
    if o.strip()
]

# ---------------------------------------------------------------------------
# Content Security Policy
# ---------------------------------------------------------------------------

CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", 'https://cdn.yektanet.com', 'https://cdn.ampproject.org'),
        'style-src': ("'self'", "'unsafe-inline'"),  # inline styles used in templates
        'frame-src': ("'self'", 'https://cdn.ampproject.org'),
        'img-src': ("'self'", 'data:', 'https:', 'https://cdn.ampproject.org'),
        'font-src': ("'self'", 'data:'),
        'connect-src': ("'self'",),
    },
}

# ---------------------------------------------------------------------------
# Auth / passwords
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# I18N
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ('fa', _('Persian')),
    ('en', _('English')),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

# ---------------------------------------------------------------------------
# Third-party app settings
# ---------------------------------------------------------------------------

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

CAPTCHA_FONT_SIZE = 30
CAPTCHA_LETTER_ROTATION = (-35, 35)
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'

# Optional: enable when Redis (or LocMem) is ready and django_ratelimit is wanted
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'webjin-cache',
#     }
# }
