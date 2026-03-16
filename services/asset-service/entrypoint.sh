#!/bin/bash
set -e

export PYTHONPATH=$PYTHONPATH:/app/src

# Run Tests
if [[ "$RUN_TESTS" == "true" || "$1" == "pytest" ]]; then
    echo "Running tests..."
    [[ "$1" == "pytest" ]] && shift # remove 'pytest' from args if present
    exec pytest src/assets/tests "$@"

# Run cli
elif [[ "$1" == "cli" ]]; then
    echo "Running CLI..."
    shift
    exec python3 -m assets.cli "$@"

# Handle alembic
elif [[ "$1" == "alembic" || "$1" == "bash" ]]; then
    echo "Running alembic migrations..."
    ALEMBIC_PATH=$(which alembic)
    shift
    exec "$ALEMBIC_PATH" "$@"

else
    echo "Starting Gunicorn..."
    exec gunicorn \
          --reload \
          --reload-engine=poll \
          --bind 0.0.0.0:8080 \
          --access-logfile - \
          --error-logfile - \
          assets.main:app
fi