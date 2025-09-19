# # Start with a base image containing Python 3.11
# FROM python:3.11

# # Set the working directory in the Docker image
# WORKDIR /

# # Install dependencies
# COPY requirements.txt .
# RUN apt-get update && apt-get upgrade -y && apt-get install -y libpq-dev postgresql-client nginx build-essential
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# # Copy the Django app to the container
# COPY . .

# # Copy the Nginx config file
# #COPY nginx/default.conf /etc/nginx/sites-enabled/
# COPY nginx.conf /etc/nginx/nginx.conf


# # Expose port 80 for Nginx traffic
# EXPOSE 80

# # Define environment variables

# ENV POSTGRES_USER=unsql_admin
# ENV POSTGRES_PASSWORD=OZpb3Bf4zoTslo
# ENV POSTGRES_DB=postgres
# ENV POSTGRES_HOST=unsql-postgres.postgres.database.azure.com


# ENV ASSETS_ROOT=/static/assets


# ENV AUTH0_CLIENT_ID=nEYg15ldJKH3kPzf6n4uMxg5txakUl2D
# ENV AUTH0_CLIENT_SECRET=nvBqfST6psXX7W3PAFMwp-JN7ZHwgccUfcq_ryZTEFUeBv0WvSYDO-bPPIJeU-c4
# ENV AUTH0_DOMAIN=dev-glybdgntuacarzbb.us.auth0.com

# ENV AUTH0_MACHINE_ID=SIFZfaIUZMDHWYdFK8Vr6SaTrSdJCYKG
# ENV AUTH0_MACHINE_DOMAIN=dev-glybdgntuacarzbb.us.auth0.com
# ENV AUTH0_MACHINE_SECRET=NclqZmNBn-7qW7NtuhKEZEdyBvJqpxmSvLAgC16kuOM1n2AStUTYMJwPD7xKyjxz

# ENV AUDIENCE=dev-glybdgntuacarzbb.us.auth0.com

# ENV STRIPE_PUBLISHABLE_KEY=pk_test_51H4rQIExPGKy6MgXI5BSpwpzYdeW5p7a7HemlkDi0Asd0OU01R9JIZqNgK9Vh2gyoq9Tiyc48BaWVeVaBpEHkb1N00YiXuGL3Z
# ENV STRIPE_SECRET_KEY=sk_test_51H4rQIExPGKy6MgXTzuh72WSaLbxV95K1jB3RrwGZwGfRQPfzZK23XDbzRIIVJXQ3GLvDBjVH8kdEuNolAgmzMem00ODBddiWi
# ENV STRIPE_ENDPOINT_SECRET=whsec_3mfNrDkUPP3Q5epmlKrw9iPsyIi1VnpD

# ENV STRIPE_PRODUCT_SOLO=prod_OGVmN9eQqj2jYn
# ENV STRIPE_PRICE_SOLO=price_1NTylEExPGKy6MgXvRVjlsqo
# #ENV STRIPE_PRODUCT_SOLO=prod_O0lQ7aZ79JXpsf
# #ENV STRIPE_PRICE_SOLO=price_1NEjtgExPGKy6MgXeanmKnoh
# ENV STRIPE_PRODUCT_TEAM_STARTER=prod_O0lQ8YOUjddsKU
# ENV STRIPE_PRICE_TEAM_STARTER=price_1NEjtzExPGKy6MgXGFPT0ljQ

# ENV FERNET_KEY=7fVsiG6U_isOUpu4ccVRuaOxLhYvCxkU4Sg4wMILRG0=
# ENV DJANGO_SETTINGS_MODULE=core.settings.local


# # Start Nginx and the Django app
# CMD ["sh", "-c", "\
#   until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p 5432 -c '\\q'; do \
#     >&2 echo 'Postgres is unavailable - sleeping'; \
#     sleep 1; \
#   done; \
#   >&2 echo 'Postgres is up - executing command'; \
#   python manage.py collectstatic --no-input; \
#   python manage.py makemigrations; \
#   python manage.py makemigrations accounts; \
#   python manage.py makemigrations authentication; \
#   python manage.py makemigrations home; \
#   python manage.py migrate; \
#   gunicorn -c ./gunicorn-cfg.py core.wsgi:application & \
#   nginx -g 'daemon off;' || (echo 'Nginx failed to start' && cat /var/log/nginx/error.log); \
# "]


# Start with a base image containing Python 3.11
FROM python:3.11

# Set the working directory in the Docker image
WORKDIR /apps

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y && apt-get install -y libpq-dev postgresql-client nginx build-essential
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the Django app to the container
COPY . .


# Expose port 80 for Nginx traffic
EXPOSE 8000

# Define non-sensitive environment variable
ENV DJANGO_SETTINGS_MODULE=core.settings.local

# Start Nginx and the Django app
CMD ["sh", "-c", "until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p 5432 -c '\\q'; do >&2 echo 'Postgres is unavailable - sleeping'; sleep 1; done; >&2 echo 'Postgres is up - executing command'; python /apps/manage.py collectstatic --no-input; python /apps/manage.py makemigrations; python /apps/manage.py makemigrations accounts; python /apps/manage.py makemigrations authentication; python /apps/manage.py makemigrations home; python /apps/manage.py migrate; gunicorn -c /apps/gunicorn-cfg.py core.wsgi:application"]