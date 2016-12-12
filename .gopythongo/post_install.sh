#!/usr/bin/env bash

# add the radicale user and group if it doesn't exist yet
adduser --home /run/radicale --disabled-login --disabled-password --system --group radicale

# the following was assembled from various default blocks created by dh_make helpers
# in packages using the default deb build system
if [ -x "/usr/bin/deb-systemd-helper" ]; then
    # unmask if previously masked by apt-get remove
    /usr/bin/deb-systemd-helper unmask radicale.service >/dev/null || true

    if /usr/bin/deb-systemd-helper --quiet was-enabled radicale.service; then
        # Enables the unit on first installation, creates new
        # symlinks on upgrades if the unit file has changed.
        deb-systemd-helper enable radicale.service >/dev/null || true
    else
        # Update the statefile to add new symlinks (if any), which need to be
        # cleaned up on purge. Also remove old symlinks.
        deb-systemd-helper update-state radicale.service >/dev/null || true
    fi
fi

if [ -d /run/systemd/system ] ; then
    # make sure tempfiles exist
    systemd-tmpfiles --create /usr/lib/tmpfiles.d/radicale.conf >/dev/null || true
fi
