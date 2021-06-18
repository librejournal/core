#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

celery -A coreapp.coreapp worker -l info -c 2
