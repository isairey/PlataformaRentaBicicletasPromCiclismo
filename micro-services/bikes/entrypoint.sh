#!/bin/sh
set -e

echo "Running database migrations..."
python -m flask db upgrade

echo "Starting server..."
exec python -m flask run --host=0.0.0.0 --port=8080
