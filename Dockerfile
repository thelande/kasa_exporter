FROM python:3.9-alpine

WORKDIR /usr/src/app
COPY requirements.txt kasa-exporter.py ./

RUN set -eux; \
    apk add --no-cache \
        pcre \
    ; \
    apk add --no-cache --virtual .build-deps \
        build-base \
        linux-headers \
        pcre-dev \
    ; \
    pip install -q --no-cache-dir --progress-bar off \
        -r requirements.txt \
        uwsgi \
    ; \
    apk del .build-deps

EXPOSE 9907
ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:9907", "--wsgi-file", "kasa-exporter.py", "--callable", "app"]
