r"""

    sparkles.settings
    ~~~~~~~~~~~~~~~~~

    This file is used to configure Django.

"""

import os
import sys
from datetime import timedelta
from os.path import abspath, dirname, join, exists
project_root = dirname(abspath(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
SECRET_KEY = "please change me to some wacky random value"
STATIC_ROOT = "/opt/sparkles/static"
STATIC_URL = "/static/"
SITE_ID = 1
DEFAULT_CHARSET = "utf-8"
USE_I18N = True
USE_L10N = False
USE_THOUSAND_SEPARATOR = True
USE_TZ = True
TIME_ZONE = "US/Eastern"
ROOT_URLCONF = "sparkles.urls"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
USE_X_FORWARDED_HOST = True

BOLD = "\x1b[1m"
GREEN = "\x1b[32m"
RESET = "\x1b[0m"

ADMINS = (
    ("", "jtunney@lobstertech.com"),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "sparkles.sqlite3",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_PREFIX": project_root,
        "LOCATION": [
            "127.0.0.1:11211",
        ],
    },
}

TEMPLATE_LOADERS = (
    ("django.template.loaders.cached.Loader", (
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    )),
)

MIDDLEWARE_CLASSES = [
    "sparkles.middleware.XForwardedForMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "sparkles.middleware.CsrfCookieWhenLoggedIn",
    "sparkles.middleware.NeverCache",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.debug",
    "django.contrib.messages.context_processors.messages",
]

INSTALLED_APPS = [
    "sparkles",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    'django.contrib.staticfiles',
    "django.contrib.sessions",
    "django.contrib.admin",
    "south",
    # "reversion",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": (GREEN + "%(asctime)s %(levelname)s %(name)s "
                       "%(filename)s:%(lineno)d " + RESET + "%(message)s"),
        },
        "simple": {
            "format": GREEN + "%(levelname)s " + RESET + "%(message)s",
        },
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "django.utils.log.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        "django": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": True,
        },
        "django.request": {
            "level": "WARNING",
            "handlers": ["console", "mail_admins"],
            "propagate": False,
        },
        "sparkles": {
            "level": "WARNING",
            "handlers": ["console", "mail_admins"],
            "propagate": False,
        },
    },
}

try:
    from sparkles.settings_local import *
except ImportError:
    pass
