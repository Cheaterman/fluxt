#!/bin/sh
docker compose up -d &&
(
    sleep .25 &&
    echo -e "\n\n\t\e[32m✔\e[0m Fluxt is listening on http://0.0.0.0:8080\n\n" &
) &&
uwsgi \
    --master \
    --plugin http \
    --plugin router_http \
    --http :8080 \
    --route '.* httpdumb:proxy_run/nginx.sock' \
    --http-raw-body \
    --offload-threads 4 \
    -z 3600 \
    --http-timeout 3600 \
    --workers 4 \
    --threads 64 \
    --ignore-sigpipe \
    --ignore-write-errors \
;
