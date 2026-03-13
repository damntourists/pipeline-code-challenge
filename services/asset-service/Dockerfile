FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    && rm -rvf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY common /tmp/common
RUN pip install /tmp/common

FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends && rm -rvf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY common /tmp/common

COPY services/asset-service/ .

RUN pip install -e .

COPY services/asset-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
