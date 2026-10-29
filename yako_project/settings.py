"""Standalone Django host for AI YAKO. PostgreSQL only."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

def required(name):
    value = os.getenv(name, '').strip()
    if not value:
        raise ImproperlyConfigured(f'Missing environment variable: {name}')
    return value

def csv_env(name, default=''):
    return [x.strip() for x in os.getenv(name, default).split(',') if x.strip()]

SECRET_KEY = required('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'false').lower() == 'true'
ALLOWED_HOSTS = csv_env('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
CSRF_TRUSTED_ORIGINS = csv_env('DJANGO_CSRF_TRUSTED_ORIGINS')
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_qvac_financial.apps.AIYakoConfig',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'yako_project.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'yako_project.wsgi.application'
ASGI_APPLICATION = 'yako_project.asgi.application'
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': required('POSTGRES_DB'),
    'USER': required('POSTGRES_USER'),
    'PASSWORD': required('POSTGRES_PASSWORD'),
    'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'PORT': os.getenv('POSTGRES_PORT', '5432'),
    'CONN_MAX_AGE': 60,
}}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'false').lower() == 'true'
