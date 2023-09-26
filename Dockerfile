# AUTHOR:           Clay Teeter <teeterc@gmail.com>, Nicholas Long <nicholas.long@nrel.gov>
# DESCRIPTION:      Image with seed platform and dependencies running in development mode
# TO_BUILD_AND_RUN: docker-compose build && docker-compose up

FROM python:3.9-slim

RUN apt-get update -qq && apt-get upgrade -y -qq
RUN apt-get install -y -qq \
        libpq-dev \
        libgdal-dev \
        python3-dev \
        python3-psycopg2 \
        nginx \
<<<<<<< HEAD
        git \
        npm && \
=======
        openssl-dev \
        geos-dev \
        gdal \
        gcc \
        musl-dev \
        cargo \
        tzdata && \
>>>>>>> merging_new_version
    ln -sf /usr/bin/python3 /usr/bin/python && \
    pip3 install --upgrade pip setuptools && \
    pip3 install supervisor==4.2.2 && \
    pip3 install uwsgi && \
    ln -sf /usr/local/bin/uwsgi /usr/bin/uwsgi && \
    mkdir -p /var/log/supervisord/ && \
    rm -r /root/.cache && \
    addgroup --gid 1000 uwsgi && \
    adduser --system --ingroup uwsgi --uid 1000 uwsgi && \
    mkdir -p /home/uwsgi/.ssh && \
    mkdir -p /run/nginx

## Note on some of the commands above:
##   - create the uwsgi user and group to have id of 1000
##   - copy over python3 as python
##   - pip install --upgrade pip overwrites the pip so it is no longer a symlink
##   - coreutils is required due to an issue with our wait-for-it.sch script:
##     https://github.com/vishnubob/wait-for-it/issues/71

### Install python requirements
WORKDIR /seed
COPY ./requirements.txt /seed/requirements.txt
COPY ./requirements/*.txt /seed/requirements/
RUN pip uninstall -y enum34
RUN --mount=type=secret,id=ssh-key,target=/home/uwsgi/.ssh/id_rsa pip3 install --prefer-binary -r requirements/aws.txt

### Install JavaScript requirements - do this first because they take awhile
### and the dependencies will probably change slower than python packages.
### README.md stops the no readme warning
COPY ./package.json /seed/package.json
COPY ./vendors/package.json /seed/vendors/package.json
COPY ./README.md /seed/README.md
# unsafe-perm allows the package.json postinstall script to run with the elevated permissions
RUN npm install --unsafe-perm

### Copy over the remaining part of the SEED application and some helpers
WORKDIR /seed
COPY . /seed/
COPY ./docker/wait-for-it.sh /usr/local/wait-for-it.sh
RUN git config --system --add safe.directory /seed

# nginx configuration - replace the root/default nginx config file and add included files
COPY ./docker/nginx/*.conf /etc/nginx/
# symlink maintenance.html that nginx will serve in the case of a 503
RUN ln -sf /seed/collected_static/maintenance.html /var/www/html/maintenance.html
# set execute permissions on the maint script to toggle on and off
RUN chmod +x ./docker/maintenance.sh

# Supervisor looks in /etc/supervisor for the configuration file.
COPY ./docker/supervisor-seed.conf /etc/supervisor/supervisord.conf

# entrypoint sets some permissions on directories that may be shared volumes
COPY ./docker/seed-entrypoint.sh /usr/local/bin/seed-entrypoint
RUN chmod 775 /usr/local/bin/seed-entrypoint
ENTRYPOINT ["seed-entrypoint"]

CMD ["supervisord"]

EXPOSE 80
