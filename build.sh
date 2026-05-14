#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Créer le superadmin automatiquement s'il n'existe pas
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mhechange.dj', 'pastinio2023ZES')
    print('Superuser créé.')
else:
    print('Superuser existe déjà.')
"
