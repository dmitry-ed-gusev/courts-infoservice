"""
    Django settings for Courts Info project.
    Generated by 'django-admin startproject' using Django 4.1.2.

    Useful info:
        - https://docs.djangoproject.com/en/4.1/topics/settings/
        - (list of settings) https://docs.djangoproject.com/en/4.1/ref/settings/

    Created:  Dmitrii Gusev, 16.10.2022
    Modified: Dmitrii Gusev, 17.10.2022
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Used for a default title
APP_TITLE = 'Все суды РФ'
APP_NAME = 'Информация о судебных делах РФ'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-q)33m-yhqo*(%tx#z*zo()yj*3lq94-*5+5(1c@s^vd)q6tn6h"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # todo: check this setting!


# Application definition

INSTALLED_APPS = [

    # - django applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # - django installed extensions
    'django.contrib.humanize',
    'django_extensions',
    'crispy_forms',
    'rest_framework',
    'social_django',
    'taggit',

    # - our custom applications
    'home.apps.HomeConfig',  # application for the site [Home/Main Page]
    'courts.apps.CourtsConfig',  # application for the [Courts Info Page]
    'stats.apps.StatsConfig',  # application for the [Statistics Info Page]

]

# When we get to crispy forms :)
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# When we get to tagging
TAGGIT_CASE_INSENSITIVE = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "courtsinfo.urls"

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

                'home.context_processors.settings',  # new added
                'social_django.context_processors.backends',  # new added
                'social_django.context_processors.login_redirect',  # new added
            ],
        },
    },
]

WSGI_APPLICATION = "courtsinfo.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {

    'mysql': {  # MySql DB (hosting)
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zzzzz',
        'USER': 'xxxxx',
        'PASSWORD': 'ccccc',
        'HOST': '<db host>',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },

    "default": {  # simple sqlite database (testing)
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization: https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "ru"  # "en-us" <- original encoding

TIME_ZONE = "EET"  # "UTC" <- default setting, EET - same as MSK -> GMT+3

USE_I18N = True

USE_L10N = True  # newly added

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# todo: social login implementation
# # Configure the social login
# try:
#     from . import github_settings
#     SOCIAL_AUTH_GITHUB_KEY = github_settings.SOCIAL_AUTH_GITHUB_KEY
#     SOCIAL_AUTH_GITHUB_SECRET = github_settings.SOCIAL_AUTH_GITHUB_SECRET
# except:
#     print('When you want to use social login, please see dj4e-samples/github_settings-dist.py')

# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html#authentication-backends
# https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html
# AUTHENTICATION_BACKENDS = (
#     'social_core.backends.github.GithubOAuth2',
#     # 'social_core.backends.twitter.TwitterOAuth',
#     # 'social_core.backends.facebook.FacebookOAuth2',

#     'django.contrib.auth.backends.ModelBackend',
# )

LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Don't set default LOGIN_URL - let django.contrib.auth set it when it is loaded
# LOGIN_URL = '/accounts/login'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# logging configuration for django, see more:
#   - https://docs.djangoproject.com/en/4.0/topics/logging/
#   - https://docs.djangoproject.com/en/4.0/ref/logging/#default-logging-configuration
#   - https://docs.djangoproject.com/en/4.0/howto/logging/#logging-how-to
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {  # logging formatters

        "standard": {  # standard log format
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },

        "simple": {  # usually used log format
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },

        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },

    },  # end of formatters block

    "handlers": {  # logging handlers

        "default": {  # default handler (for emergency cases)
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },

        "console": {  # usual console handler
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },

        "std_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": str(BASE_DIR) + "/log_info.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 20,
            "encoding": "UTF-8",
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": str(BASE_DIR) + "/log_errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 20,
            "encoding": "UTF-8",
        },

    },  # end of handlers block

    "loggers": {  # defining logger block

        'django': {  # dedicated django logger - log only to console
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },

        'parso': {  # django shell parser/autocomplete, it worth to have it upper DEBUG
            'level': 'INFO',  # todo: set to WARN?
        },

        "rallytool": {  # todo: logger for some library used
            # 'handlers': ['default'],
            "level": "DEBUG",
            # 'propagate': False
        },

        "__main__": {  # if __name__ == '__main__' - emergency case!!!
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },

    },  # end of loggers module

    "root": {  # root logger
        "level": "DEBUG",  # todo: should be WARNING for PROD?
        "handlers": ["console", "std_file_handler", "error_file_handler"],
    },

}  # end of LOGGING block

# https://coderwall.com/p/uzhyca/quickly-setup-sql-query-logging-django
# https://stackoverflow.com/questions/12027545/determine-if-django-is-running-under-the-development-server

'''  # Leave off for now
import sys
if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
    print('Running locally')
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }
'''