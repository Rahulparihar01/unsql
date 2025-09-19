# move this to root directory to run w/ docker-compose

FROM python:3.11

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# install python dependencies
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["./entrypoint.sh", "unsql-postgres.postgres.database.azure.com"]
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]