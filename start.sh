#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

python manage.py migrate

gunicorn -w ${NUM_WORKERS:-2} \
 --worker-class gevent \
 --threads 5 \
 --bind 0.0.0.0:${PORT:-5050} \
 coreapp.coreapp.wsgi:application
