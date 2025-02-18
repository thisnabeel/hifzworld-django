"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from decouple import config
import dj_database_url

# Determine environment
ENVIRONMENT = config('DJANGO_ENV', 'development')
# DEBUG = ENVIRONMENT == 'development'
DEBUG=True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ASGI Application
ASGI_APPLICATION = 'api.asgi.application'

# Security settings
SECRET_KEY = config('SECRET_KEY')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Fix for infinite redirects
SECURE_SSL_REDIRECT = False  # Disable HTTPS forced redirection (Render already handles it)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Trust Render proxy headers

# Allowed hosts
ALLOWED_HOSTS = [
    "hifzworld.onrender.com",
    "localhost",
    "127.0.0.1",
]

# Application definition
INSTALLED_APPS = [
    'django_extensions',
    'corsheaders',
    'user_page',
    'mushaf_page',
    'mushaf_segment',
    'mushaf',
    'missions',
    'django.contrib.admin',
    'accounts',
    'lead',
    'branch',
    'events',
    'user_grants',
    'user_progress_report',
    'channels',
    'daphne',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTH_USER_MODEL = 'accounts.User'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "https://hifzworld.onrender.com",
    "https://hifzworld-svelte-thisnabeel.vercel.app",
    "https://www.hifz.world"
]

CORS_ALLOW_METHODS = [
    "DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"
]

CORS_ALLOW_HEADERS = [
    "accept", "accept-encoding", "authorization", "content-type",
    "dnt", "origin", "user-agent", "x-csrftoken", "x-requested-with",
    "cache-control", "pragma"
]

# Root URL configuration
ROOT_URLCONF = 'api.urls'

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'api.wsgi.application'

# Database Configuration
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security Headers
SECURE_HSTS_SECONDS = 31536000  # Keep this for security
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static file settings
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AWS Storage Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
