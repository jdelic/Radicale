#!/usr/bin/env bash

if [ "$1" = "remove" ]; then
    if [ -x "/usr/bin/deb-systemd-helper" ]; then
        /usr/bin/deb-systemd-helper mask radicale.service >/dev/null
    fi
fi

if [ "$1" = "purge" ]; then
    deluser --system radicale
    delgroup --system radicale

    if [ -x "/usr/bin/deb-systemd-helper" ]; then
        /usr/bin/deb-systemd-helper purge radicale.service >/dev/null
        /usr/bin/deb-systemd-helper unmask radicale.service >/dev/null
    fi
fi
