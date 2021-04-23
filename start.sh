#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

python manage.py migrate

gunicorn coreapp.coreapp.wsgi:application --bind 0.0.0.0:$PORT
