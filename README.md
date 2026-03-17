# pipeline-code-challenge

LAIKA Pipeline Engineering coding challenge.

This project contains:

- `common/` — shared Python package (`asset-common`)
- `services/asset-service/` — asset validation, persistence, CLI, and API service
- `sample_data/` — sample JSON files for loading assets
- `compose.yaml` — local Docker Compose stack for MySQL and service containers

## Overview
The asset service supports:
- Validating asset and asset version data
- Storing assets and versions in a relational database
- Loading data from JSON
- Interaction through a Flask REST API

## Prerequisites

### Local virtualenv workflow
- Python 3.12
- `venv` or `virtualenv`
- MySQL available locally or via Docker

### Docker workflow
- Docker
- Docker Compose

### Optional HTTPS and reverse proxy
- `mkcert`
- `libnss3-tools`

## Environment setup
Copy the example environment file like below
```shell
cp .env.example .env
```
For local virtualenv usage, set the database host to `localhost` in `.env`.
```shell
DATABASE_URL=mysql+pymysql://dbuser:Password123@localhost:3306/asset_db
```

For Docker Compose usage, the asset service connects to the MySQL container using the hostname `db`.


## Local virtualenv setup
From the repository root, run the following:
```shell
python -m venv .venv
source .venv/bin/activate
```
Install the common package and asset service in editable mode:
```shell
pip install -e ./common
pip install -e ./services/asset-service
```

### Start MySQL for local development
If you already have MySQL running locally, make sure the `asset_db` database exists.

If you want to use the project database docker container, you may start it with the following:

```shell
docker compose up -d db
```

### Apply database migration locally
Before running the CLI or REST API, you must first apply the schema migrations:
```shell
cd services/asset-service
alembic upgrade head 
cd ../..
```

### Run the CLI locally
Run the following from the repository root where the virtualenv is activated:
```shell
python -m assets.cli --help
```

#### Example commands:
```shell
python -m assets.cli load sample_data/asset_data.json
python -m assets.cli list
python -m assets.cli add hero character modeling
python -m assets.cli get hero character
python -m assets.cli versions add hero character modeling 2 active
python -m assets.cli versions get hero character modeling 2
python -m assets.cli versions list hero character
```


### Run tests locally
From the repository root with the virtualenv activated, run:
```shell
pytest services/asset-service/src/assets/tests -q
```

### Run the Flask API locally
From the repository root with the virtualenv activated, run:
```shell
python -m assets.main
```

You can check the health status to verify it's working at http://localhost:8080/health

## Docker Compose workflow
Build the images:
```shell
docker compose build
```

Start the stack:
```shell
docker compose up -d
```
This will start the following containers: `db`, `assetsvc`, `traefik`, `dozzle`.

### Apply migrations in Docker
Run Alembic migrations inside the assetsvc container:
```shell
docker compose run --rm assetsvc alembic upgrade head
```

### Load sample data in via Docker
Example:
```shell
docker compose run --rm -v $(pwd)/sample_data/asset_data.json:/app/asset_data.json assetsvc cli load asset_data.json
```


### Run tests in Docker
Run tests with the following:
```shell
docker compose --profile test run --rm assetsvc pytest services/asset-service/src/assets/tests
```
or
```shell
docker compose --profile test run --rm assetsvc-test
```

#### Useful Docker commands:
Show logs:
```shell
docker compose logs -f assetsvc
```

Open a shell to the assetsvc container:
```shell
docker compose exec assetsvc /bin/bash 
```

Shut down the stack:
```shell
docker compose down
```

Shut down the stack and remove volumes:
```shell
docker compose down -v
```


## REST API endpoints
Health check:
```
GET /health
```

Load sample data from JSON:
```
POST /assets/load
```

Create an asset:
```
POST /assets
```

Create an asset version:
```
POST /assets/versions
```

List all assets or filter by asset name and type:
```
GET /assets
GET /assets?asset=hero&type=character
```

List all versions of an asset or retrieve a specific version:
```
GET /assets/versions?asset=hero&type=character
GET /assets/versions?asset=hero&type=character&department=modeling
GET /assets/versions?asset=hero&type=character&department=modeling&version=2
```

## SSL and local HTTPS setup
To enable local HTTPS with Traefik and localhost certificates:
```shell
sudo apt install mkcert libnss3-tools
mkcert -install
mkdir -p certs
cd certs
mkcert "*.localhost" localhost
```

Once certificates are generated and the Docker stack is running, these URLs are intended to be available:
- The asset service: https://asset.localhost
- Reverse proxy & load balancer: https://traefik.localhost
- Logging: https://dozzle.localhost


## Logging and request tracing
The service logger supports request-scoped logging through the X-Request-Id header.

When requests pass through Traefik and include X-Request-Id, that value is carried into the Flask request context and added to service logs. This makes it easier to search related events in Dozzle and follow a single request through the service logs in chronological order.

## Troubleshooting
### Local CLI cannot connect to MySQL
If the application is trying to connect to host db while running from your local virtual environment, your .env is using the Docker hostname instead of localhost.
For local usage, set:
```
DATABASE_URL=mysql+pymysql://dbuser:Password123@localhost:3306/asset_db
```
For docker usage, set:
```
DATABASE_URL=mysql+pymysql://dbuser:Password123@db:3306/asset_db
```

### Tables do not exist
Apply Alembic migrations before using the CLI or API:
```shell
cd services/asset-service
alembic upgrade head
```

### Import errors for local packages
Reinstall the packages in editable mode:
```shell
pip install -e ./common
pip install -e ./services/asset-service
```

---

## What could be better?
- Add more tests
- Add more validation
- Add more logging
- Add more error handling
- Add more documentation
- Add more comments
- Replace Dozzle logging with something like Jaeger for better tracing/observability
- Possibly separate validation into a separate service