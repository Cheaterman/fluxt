#!/bin/sh
docker-compose up -d &&
uwsgi \
    --master \
    --http :8080 \
    --route '.* http:proxy_run/nginx.sock' \
;
