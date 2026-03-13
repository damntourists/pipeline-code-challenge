#!/bin/bash
set -e

export PYTHONPATH=$PYTHONPATH:/app/src

if [[ "$RUN_TESTS" == "true" || "$1" == "pytest" ]]; then
    echo "Running tests..."
    if [[ "$1" == "pytest" ]]; then
        exec "$@"
    else
        exec pytest src/assets/tests
    fi
else
    echo "Starting Gunicorn..."
    exec gunicorn \
          --reload \
          --reload-engine=poll \
          --reload-extra-file /tmp/common/src/asset_common \
          --bind 0.0.0.0:8080 \
          --access-logfile - \
          --error-logfile - \
          assets.main:app
fi