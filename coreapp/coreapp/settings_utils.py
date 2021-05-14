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
