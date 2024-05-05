# Upwork Proposal Supporting Material

This headless app allows adding physicians with addresses in California and allows searching for the nearest physician by zip code. It comes with some sample data. Zip code lat/long values are from [geonames.org](https://geonames.org) (TIGER data can technically give us those as well).

## Running the app
`docker compose up -d`

Wait until everything is completed (this will take a while because the scripts download and insert all the TIGER data into PostGIS for geocoding addresses in California). It takes about 20 minutes on my Apple M1 Pro machine.

To see what scripts are run during every startup, check `./run.sh`. The `./db/init.sh` script is only run on the first startup (or after the db container is recreated -- e.g., by running `docker compose down` followed by `docker compose up`)

Note: The docker containers use bind mounted volumes exclusively for the app's code and scripts, so any changes made in the containers or locally on your host machine will reflect on the other end.

### Finding a physician

In a browser window, visit http://127.0.0.1:5000/94105 (a San Francisco zip code) and note the output (e.g., "Your nearest physicians are Dr. Francis from San Francisco").

Additional physicians may be found by entering different zip codes in the address bar. For example, to find Dr. Yi, enter a Yreka-area zip code, such as 96097 (i.e., visit http://127.0.0.1:5000/96097).

### Adding a physician

In a terminal window, run:

```
curl -X POST -H "Content-Type: application/json" -d '{"name": "Dr. House", "address": "123 Main St, Huntington Beach, CA"}' 127.0.0.1:5000/physician
```

Note that only California addresses will work at this time because we are only downloading geocoding data for California.

## Shelling into containers

You can shell into either container using docker compose. Note that the flaskapp container does not have bash, so you have to use `sh` instead.

For example, to shell into the `db` container to query the database directly:

    $ docker compose exec -ti db bash
    % psql -U postgres

To shell into the `flaskapp` container to run commands against flask or the pipenv/virtualenv directly:

    $ docker compose exec -ti flaskapp sh
    % cd /usr/src/app
    % pipenv run flask shell

Or

    % pipenv run flask db migrate

## Creating and running migrations

Modify or add models to app.py. Then, in the `flaskapp` container, run `pipenv run flask db migrate`. Inspect the resulting migration file under `./migrations/versions` to ensure it will do as you expect. Edit as necessary. Then run `pipenv run flask db upgrade`.

Be sure to update `seed.py` if necessary (i.e., if your migration modifies the zip_code or physician tables).

## Installing additional pip packages

In the `flaskapp` container, run `pipenv install $YOUR_PACKAGE_NAME`.
