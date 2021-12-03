#!/bin/sh
docker-compose up -d &&
uwsgi \
    --master \
    --plugin http \
    --plugin router_http \
    --http :8080 \
    --route '.* http:proxy_run/nginx.sock' \
    -z 3600 \
    --workers 4 \
    --threads 64 \
    --ignore-sigpipe \
    --ignore-write-errors \
;
