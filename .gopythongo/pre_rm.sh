#!/usr/bin/env bash

deb-systemd-invoke stop radicale > /dev/null || true

find /usr/local/radicale/lib -name \*.pyc -delete
find /usr/local/radicale -type d -name __pycache__ -print0 | xargs -0 rm -rf
find /usr/local/radicale -type d -name static -print0 | xargs -0 rm -rf
