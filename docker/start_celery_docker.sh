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
/usr/local/wait-for-it.sh --strict $REDIS_ACTUAL_HOST:$REDIS_PORT

# check if the number of workers is set in the env
if [ -z ${NUMBER_OF_WORKERS} ]; then
    echo "var is unset"
    # Set the number of workers to half the number of cores on the machine
    export NUMBER_OF_WORKERS=$(($(nproc) / 2))
    export NUMBER_OF_WORKERS=$(($NUMBER_OF_WORKERS>1?$NUMBER_OF_WORKERS:1))
fi

echo "Number of workers will be set to: $NUMBER_OF_WORKERS"
celery -A seed worker -l info -c $NUMBER_OF_WORKERS --maxtasksperchild 1000 --uid 1000 --events
