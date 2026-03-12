# pipeline-code-challenge
LAIKA Pipeline Engineering Coding Challenge

## First run
```shell
cp .env.example .env
```

## SSL (optional)
```shell
sudo apt install mkcert libnss3-tools
mkcert -install
mkdir -p certs && cd certs
mkcert "*.localhost" localhost
```