#!/bin/bash

set -e

# Source Environment Variables
source core/env/prod/.env

# Update package list and upgrade all packages
apt-get update
apt-get upgrade -y

# Install python, pip, and your project's dependencies
apt-get install -y python3.11 python3-pip postgresql-client
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Install and configure Nginx
apt-get install -y nginx
rm /etc/nginx/sites-enabled/default
cp ./nginx/nginx.conf /etc/nginx/sites-enabled/
service nginx start

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -p 5432 -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing command"

# Apply Django migrations
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py makemigrations accounts
python manage.py makemigrations authentication
python manage.py makemigrations home
python manage.py migrate

# Run the Gunicorn server

