#!/bin/sh
until pg_isready -h orders_db -p 5432; do
  sleep 1
done

python manage.py migrate
python manage.py collectstatic --noinput


# start daphne server
daphne -b 0.0.0.0 -p 8000 orders_service.asgi:application