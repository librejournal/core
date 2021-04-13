import os

from django.db.backends import postgresql

def get_local_db_conf() -> dict:
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USERNAME"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOSTNAME"],
        "PORT": os.environ["DB_PORT"],
    }