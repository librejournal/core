import os

SERVICE_CONSTANTS = {
    "files": {
        "url": os.environ.get("FILES_SERVICE_URL", ""),
        "access_token": os.environ.get("FILES_SERVICE_ACCESS_TOKEN", ""),
    },
    "core": {
        "url": os.environ.get("CORE_SERVICE_URL", ""),
        "access_token": os.environ.get("CORE_SERVICE_ACCESS_TOKEN", ""),
    },
}

THIS_SERVICE_URL = SERVICE_CONSTANTS["core"]["url"]
THIS_SERVICE_ACCESS_TOKEN = SERVICE_CONSTANTS["core"]["access_token"]


def env_to_bool(key):
    value = os.environ.get(key, "").upper()
    if value == "TRUE":
        return True
    elif value == "FALSE":
        return False
    else:
        return None
