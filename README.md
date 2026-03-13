# pipeline-code-challenge
LAIKA Pipeline Engineering Coding Challenge

## First run
```shell
cp .env.example .env
```

# Python Library Example
### Start the MySQL server
```shell
docker-compose up -d db
```

### Start Jupyter Notebook


# REST Example

https://traefik.localhost

https://dozzle.localhost

### Configure SSL
```shell
sudo apt install mkcert libnss3-tools
mkcert -install
mkdir -p certs && cd certs
mkcert "*.localhost" localhost
```