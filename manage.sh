#!/bin/bash
set -e

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py makemigrations accounts
python manage.py makemigrations authentication
python manage.py makemigrations home
python manage.py migrate