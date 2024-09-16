from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        # "MIGRATE": False,  # Disable migrations here
    }
}

MIGRATION_MODULES = {app_label: None for app_label in INSTALLED_APPS}

SECRET_KEY = "a_very_secretive_key"
