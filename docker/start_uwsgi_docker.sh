#!/bin/bash

cd /seed

echo "Waiting for postgres to start"
if [ -v POSTGRES_HOST ];
then
   POSTGRES_ACTUAL_HOST=$POSTGRES_HOST
else
   POSTGRES_ACTUAL_HOST=db-postgres
fi
/usr/local/wait-for-it.sh --strict $POSTGRES_ACTUAL_HOST:$POSTGRES_PORT

echo "Waiting for redis to start"
if [ -v REDIS_HOST ];
then
   REDIS_ACTUAL_HOST=$REDIS_HOST
else
   REDIS_ACTUAL_HOST=db-postgres
fi
/usr/local/wait-for-it.sh --strict $REDIS_ACTUAL_HOST:6379

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
