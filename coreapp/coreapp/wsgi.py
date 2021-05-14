"""
WSGI config for coreapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


def set_up_and_get_application():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coreapp.coreapp.settings")
    return get_wsgi_application()


application = set_up_and_get_application()
