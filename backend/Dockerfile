FROM cheaterman/flask

COPY docker-entrypoint.sh /
COPY . /code

RUN \
    apk add --no-cache \
        libmagic \
    && \
    su uwsgi -c ' \
        pip install --no-cache-dir -U -r /code/requirements.txt \
    '

ENTRYPOINT ["/docker-entrypoint.sh"]
