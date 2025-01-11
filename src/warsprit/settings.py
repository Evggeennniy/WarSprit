"""
Django settings for warsprit project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-j(mnp+0fga@kkvciuk5rlnk@)^%w=-ilmc@pmb+ypqzpis)#h)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django_ckeditor_5",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "catalog",
    "colorfield"
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

ROOT_URLCONF = 'warsprit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'warsprit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Europe/Kyiv"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Директорія для збереження зібраних статичних файлів (для продакшну)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Шляхи до папок з вашими статичними файлами (для розробки)
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # наприклад, якщо ви тримаєте файли в папці static
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


LOCALE_PATHS = [
    BASE_DIR / "locale/",
]
MODELTRANSLATION_CUSTOM_FIELDS = "CKEditor5Field"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",  # Добавляем заголовки (H1, H2 и т.д.)
            "|",
            "bold",  # Жирный текст
            "italic",  # Курсив
            "underline",  # Подчеркивание
            "fontColor",  # Цвет текста
            "fontBackgroundColor",  # Цвет фона текста
        ],
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "fontColor": {
            "colors": [
                {"color": "hsl(0, 0%, 0%)", "label": "Black"},
                {"color": "hsl(0, 75%, 60%)", "label": "Red"},
                {"color": "hsl(30, 75%, 60%)", "label": "Orange"},
                {"color": "hsl(60, 75%, 60%)", "label": "Yellow"},
                {"color": "hsl(120, 75%, 60%)", "label": "Green"},
                {"color": "hsl(180, 75%, 60%)", "label": "Turquoise"},
                {"color": "hsl(240, 75%, 60%)", "label": "Blue"},
                {"color": "hsl(300, 75%, 60%)", "label": "Purple"},
            ]
        },
        "fontBackgroundColor": {
            "colors": [
                {"color": "hsl(0, 0%, 100%)", "label": "White"},
                {"color": "hsl(0, 75%, 60%)", "label": "Red"},
                {"color": "hsl(30, 75%, 60%)", "label": "Orange"},
                {"color": "hsl(60, 75%, 60%)", "label": "Yellow"},
                {"color": "hsl(120, 75%, 60%)", "label": "Green"},
                {"color": "hsl(180, 75%, 60%)", "label": "Turquoise"},
                {"color": "hsl(240, 75%, 60%)", "label": "Blue"},
                {"color": "hsl(300, 75%, 60%)", "label": "Purple"},
            ]
        },
        "language": "uk",
    }
}


DISCOUNT = 150