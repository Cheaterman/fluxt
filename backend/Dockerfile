FROM cheaterman/flask

COPY docker-entrypoint.sh /
COPY . /code

RUN \
    apk update && \
    apk add \
        libmagic \
    && \
    su uwsgi -c ' \
        pip install --no-cache-dir -U -r /code/requirements.txt \
    '

ENTRYPOINT ["/docker-entrypoint.sh"]
