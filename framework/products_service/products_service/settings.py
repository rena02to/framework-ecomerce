from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = int(os.getenv("DEBUG", "0")) == 1

CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "users_service",
    "products_service",
    "orders_service",
    "carts_service",
    "recomendations_service",
    "nginx_gateway",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cleanup.apps.CleanupConfig",
    "products",
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

ROOT_URLCONF = "products_service.urls"

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

WSGI_APPLICATION = "products_service.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Maceio"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/api/products/static/"
STATIC_ROOT = "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_X_FORWARDED_HOST = True
FORCE_SCRIPT_NAME = "/api/products"

MEDIA_URL = "/api/products/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
