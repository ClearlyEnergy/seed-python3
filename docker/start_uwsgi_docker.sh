#!/bin/bash

cd /seed

echo "Waiting for postgres to start"
/usr/local/wait-for-it.sh --strict db-postgres:5432

echo "Waiting for redis to start"
/usr/local/wait-for-it.sh --strict db-redis:6379

# collect static resources before starting and compress the assets
./manage.py collectstatic --no-input -i package.json -i npm-shrinkwrap.json -i node_modules/openlayers-ext/index.html
./manage.py compress --force

# set the permissions in the /seed/collected_static folder
chown -R uwsgi /seed/collected_static

# create label temp directory
mkdir -p /seed/src/label/label/tmp
chown -R uwsgi /seed/src/label/label/tmp

# Run any migrations before starting -- always for now
./manage.py migrate

if [[ -z $NO_CREATE_USER ]]; then
    echo "Creating default user"
    ./manage.py create_default_user --username=$SEED_ADMIN_USER --password=$SEED_ADMIN_PASSWORD --organization=$SEED_ADMIN_ORG
fi

/usr/bin/uwsgi --ini /seed/docker/uwsgi.ini
