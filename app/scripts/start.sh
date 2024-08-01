#!/bin/sh

# Copy .env file from a predefined location to the application directory
cp /path/to/secrets/subscriptionManagerBackend/.env /app/.env

# Start the Flask application
exec flask run --host=0.0.0.0 --port=8000
