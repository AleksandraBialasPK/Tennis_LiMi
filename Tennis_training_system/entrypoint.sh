#!/bin/bash

echo "----------- Collect static files -----------"
python manage.py collectstatic --no-input

echo "----------- Apply migration -----------"
python manage.py makemigrations
python manage.py migrate

echo "----------- Run django local server --------- "
python manage.py runserver 0.0.0.0:8000
