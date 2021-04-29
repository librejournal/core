import os

from django.core.wsgi import get_wsgi_application

# from coreapp.coreapp.wsgi import set_up_and_get_application

os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coreapp.settings")

application = get_wsgi_application()
