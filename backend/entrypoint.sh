#!/bin/sh
set -eu

if [ "$(id -u)" -eq 0 ]; then
    # A newly attached host disk can cover the image's owned /data directory.
    chown lantern:lantern /data
    exec setpriv --reuid=lantern --regid=lantern --init-groups --no-new-privs "$@"
fi

exec "$@"
