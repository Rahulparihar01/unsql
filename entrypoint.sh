#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

python manage.py collectstatic --no-input

# POSTGRES_HOST

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -p 5432 -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
echo "PostgreSQL started"

python manage.py makemigrations
python manage.py makemigrations accounts
python manage.py makemigrations authentication
python manage.py makemigrations home
python manage.py migrate
#python manage.py runserver 0.0.0.0:8000


echo "Running command: $cmd"
exec $cmd
echo "Command exited with status $?"

