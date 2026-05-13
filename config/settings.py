import os
from pathlib import Path
from dotenv import load_dotenv  # Add this import

from django.utils.translation import gettext_lazy as _
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# Load environment variables from .env file

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No DJANGO_SECRET_KEY set in environment variables!")

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Only allow these hosts in production
ALLOWED_HOSTS = ['dirweb.ir','www.dirweb.ir','webjin.ir','www.webjin.ir']#os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'csp',  # CSP Middleware
    'django.contrib.humanize',
    'django.contrib.sites',
    'django_cleanup',
    'captcha',
    'django_check_seo',
    'crispy_forms',
    'crispy_bootstrap5',
    # 'django_ratelimit',
    'admin_persian',
    'directory',
    'contact',
    'farsi',
    'taggit',
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'csp.middleware.CSPMiddleware',  # CSP MUST be after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
],},}]


WSGI_APPLICATION = 'config.wsgi.application'
SITE_ID = 1


if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'dirwebir_direct',
            'USER': 'dirwebir__user',
            'PASSWORD': 'mhJMq:pErC6rh',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'connect_timeout': 20,
                'read_timeout': 30,
                'write_timeout': 30,
            },
            'CONN_MAX_AGE': 60,  # Keep connections alive
    }}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
    }}

# --- Security Settings ---
# Basic Security Headers
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# SSL/HTTPS Settings
import os

SECURE_SSL_REDIRECT = not DEBUG and os.environ.get('DJANGO_ALLOWED_HOSTS') != 'localhost,127.0.0.1'  # Redirect HTTP to HTTPS in production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
  # Important for proxies

# Cookie Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # Secure in production
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG      # Secure in production

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True if not DEBUG else False
SECURE_HSTS_PRELOAD = True if not DEBUG else False

# CSP (Content Security Policy)
# --- Content Security Policy (New Format) ---
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        "default-src": ("'self'",),
        "script-src": ("'self'", 'https://cdn.yektanet.com', 'https://cdn.ampproject.org'),
        "style-src": ("'self'", "'unsafe-inline'"),
        "frame-src": ("'self'", 'https://cdn.ampproject.org'),
        "img-src": ("'self'", 'data:', 'https://cdn.ampproject.org'),
        "font-src": ("'self'",),
        "connect-src": ("'self'",),
},}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        "default-src": ("'self'",),
        "script-src": ("'self'", 'https://cdn.yektanet.com', 'https://cdn.ampproject.org'),
        "style-src": (
            "'self'",
            "'unsafe-inline'",
        ),  # 'unsafe-inline' is kept because you use inline styles in templates
        "frame-src": ("'self'", 'https://cdn.ampproject.org'),
        # Add other directives as needed, e.g., img-src, font-src
        "img-src": ("'self'", 'data:', 'https://cdn.ampproject.org'),
        "font-src": ("'self'",),
        "connect-src": ("'self'",),
},}

# Cache Configuration
# Use Redis in production, LocMem for development/testing
# if False:
#     CACHES = {
#         "default": {
#             "BACKEND": "django.core.cache.backends.redis.RedisCache",
#             "LOCATION": "redis://127.0.0.1:6379/1",
#     }}
# else:
#     # For development, we use LocMemCache.
#     # django_ratelimit will show a warning, but it will work fine for single-threaded tests.
#     CACHES = {
#         "default": {
#             "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#             "LOCATION": "unique-snowflake",  # Important: Give it a name so it's not shared with other processes
#     }}

# RatelimitCacheBackend = "django.core.cache.backends.locmem.LocMemCache"

# --- Internationalization ---
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ('fa', _('Persian')),
    ('en', _('English')),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- Crispy Forms ---
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

CAPTCHA_FONT_SIZE = 30
CAPTCHA_LETTER_ROTATION = (-35, 35)
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
