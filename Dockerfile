FROM python:3.11 as builder

WORKDIR /usr/src/app

RUN pip install --no-cache-dir --quiet --progress-bar off poetry

COPY poetry.lock pyproject.toml ./
COPY kasa_exporter ./kasa_exporter/
RUN poetry build

FROM python:3.11 as application
LABEL maintainer="Tom Helander <thomas.helander@gmail.com>"

RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt-get clean all

RUN useradd --system --shell /sbin/nologin --user-group --create-home uvicorn

COPY --from=builder /usr/src/app/dist/*.whl /tmp/
RUN pip install --quiet --no-cache-dir --progress-bar off /tmp/*.whl

COPY entrypoint.sh /usr/local/bin
EXPOSE 9907
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
