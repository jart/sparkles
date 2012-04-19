
import sys
from sparkles.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
STATIC_URL = "/static/"

TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE_CLASSES += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INSTALLED_APPS += ["debug_toolbar"]

LOGGING["loggers"]["django"]["level"] = "DEBUG"
LOGGING["loggers"]["django.request"]["level"] = "DEBUG"
LOGGING["loggers"]["sparkles"]["level"] = "DEBUG"
LOGGING["handlers"]["console"]["formatter"] = "verbose"
LOGGING["handlers"]["mail_admins"] = {"level": "DEBUG",
                                      "class": "django.utils.log.NullHandler"}

try:
    from sparkles.settings_dev_local import *
except ImportError:
    pass
