#!/bin/sh
docker-compose up -d &&
uwsgi \
    --plugin http \
    --plugin router_http \
    --master \
    --http :8080 \
    --route '.* http:proxy_run/nginx.sock' \
;
