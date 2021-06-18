"""
Django settings for coreapp project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import logging

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from .settings_utils import SERVICE_CONSTANTS, env_to_bool

logger = logging.getLogger(__name__)

ENV = os.environ.get("ENV", "local")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = Path(__file__).resolve().parent

STATIC_ROOT = PROJECT_ROOT / "static"
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    PROJECT_ROOT / "staticfiles",
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-rbvoas0kdcu-h0nyy0o5axjj20-%ueimcant=4zpe)z#7=7exc"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (ENV!="heroku")

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "coreapp.files",
    "coreapp.monetisation",
    "coreapp.stories",
    "coreapp.users",
    "coreapp.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "coreapp.utils.global_request.RequestMiddleware",
]

ROOT_URLCONF = "coreapp.coreapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "coreapp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# For local database only
try:
    DATABASES["_default_postgresql"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USERNAME"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOSTNAME"],
        "PORT": os.environ["DB_PORT"],
    }
except KeyError:
    logger.info("Env variables not set...")

if ENV == "docker_local":
    DATABASES["default"] = DATABASES["_default_postgresql"]

if ENV == "heroku":
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(
        os.environ.get("HEROKU_DATABASE_URL"),
        conn_max_age=600,
    )


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ]
}

_sendgrid_api_key = os.environ.get("SENDGRID_API_KEY", "")
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = _sendgrid_api_key
EMAIL_PORT = 587
EMAIL_USE_TLS = True

_celery_result_backend = None
_celery_broker_url = None
if ENV == "docker_local":
    _celery_result_backend = os.environ.get("CELERY_RESULT_BACKEND")
    _celery_broker_url = os.environ.get("CELERY_BROKER_URL")

if ENV == "heroku":
    _celery_result_backend = os.environ.get("REDISCLOUD_URL")
    _celery_broker_url = os.environ.get("CLOUDAMQP_URL")
    # _celery_broker_url = os.environ.get("REDISCLOUD_URL")

_celery_result_backend = _celery_result_backend or "redis://redis:6379/0"
_celery_broker_url = _celery_broker_url or "amqp://guest:guest@localhost:5672//"

CELERY_BROKER_URL = _celery_broker_url
CELERY_BROKER_POOL_LIMIT = 1
CELERY_RESULT_BACKEND = _celery_result_backend
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Istanbul"

_enable_emails = env_to_bool("ENABLE_EMAILS")
_enable_sms = env_to_bool("ENABLE_SMS")
ENABLE_EMAILS = _enable_emails is not None and _enable_emails
ENABLE_SMS = _enable_sms is not None and _enable_sms

from corsheaders.defaults import default_headers

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://files:5000",
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-pagination-limit",
    "x-pagination-offset",
]

# Accepts requests with this header as internal requests
SERVICES = SERVICE_CONSTANTS
THIS_SERVICE_ACCESS_TOKEN = SERVICES["core"]["access_token"]

MAX_REFERRALS_COUNT = 2

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
