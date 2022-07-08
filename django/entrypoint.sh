#!/bin/sh

python manage.py makemigrations main --no-input
python manage.py migrate main --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn core.wsgi:application --bind 0.0.0.0:8000