#!/bin/sh
chown -R uwsgi: /code/files &&
exec /run.py "$@"
