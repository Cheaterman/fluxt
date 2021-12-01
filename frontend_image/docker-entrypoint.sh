#!/bin/sh

socket_gid=${SOCKET_GID:-0}

(
    rm -f /run/nuxt.sock &&
    until [ -S /run/nuxt.sock ];
    do
        sleep 1;
    done;
    chgrp $socket_gid /run/nuxt.sock &&
    chmod g+w /run/nuxt.sock;
) &

exec "$@"
