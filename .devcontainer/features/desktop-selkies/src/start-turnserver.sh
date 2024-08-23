#!/bin/bash

set -e

exec turnserver \
    --verbose \
    --listening-ip="0.0.0.0" \
    --listening-ip="::" \
    --listening-port="${SELKIES_TURN_PORT:-3478}" \
    --realm="${TURN_REALM:-example.com}" \
    --channel-lifetime="${TURN_CHANNEL_LIFETIME:--1}" \
    --min-port="${TURN_MIN_PORT:-49152}" \
    --max-port="${TURN_MAX_PORT:-65535}" \
    --lt-cred-mech \
    --user="selkies:selkies" \
    --allow-loopback-peers \
    --userdb="/tmp/turnserver-turndb" \
    --pidfile="/tmp/turnserver.pid" \
    --log-file="stdout" \
    --prometheus \
    ${TURN_EXTRA_ARGS} $@
