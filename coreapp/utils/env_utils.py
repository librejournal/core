from django.conf import settings

def is_local_env():
    is_local = settings.ENV == "local"
    is_docker_local = settings.ENV == "docker_local"
    return is_local or is_docker_local
