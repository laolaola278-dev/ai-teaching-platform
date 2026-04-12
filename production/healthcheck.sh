#!/usr/bin/env bash
set -e
echo 'Healthcheck started'
curl -fsS https://localhost/health || exit 1
echo 'OK'
exit 0
