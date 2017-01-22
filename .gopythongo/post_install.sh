#!/usr/bin/env bash

# add the radicale user and group if it doesn't exist yet
adduser --home /run/radicale --disabled-login --disabled-password --system --group radicale

systemctl --system daemon-reload >/dev/null || true

# the following was assembled from various default blocks created by dh_make helpers
# in packages using the default deb build system
if [ -x "/usr/bin/deb-systemd-helper" ]; then
    # unmask if previously masked by apt-get remove
    /usr/bin/deb-systemd-helper unmask radicale.service >/dev/null || true

    if /usr/bin/deb-systemd-helper --quiet is-enabled radicale.service; then
        # If radicale had been installed before restart it (upgrade)
        deb-systemd-helper reenable radicale.service >/dev/null || true
        deb-systemd-invoke restart radicale >/dev/null || true
    else
        # on first install, disable. The admin will enable and start the service.
        deb-systemd-helper disable radicale.service > /dev/null || true
        deb-systemd-helper update-state radicale.service >/dev/null || true
    fi
fi

if [ -d /run/systemd/system ] ; then
    # make sure tempfiles exist
    systemd-tmpfiles --create /usr/lib/tmpfiles.d/radicale.conf >/dev/null || true
fi
