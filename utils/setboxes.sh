#!/bin/sh
if [ ! -L "${DESTDIR}/mss/work" ]; then
    ln -sf /mnt/mss/stuff/techy-bits/work "${DESTDIR}/mss/work"
fi

if [ ! -L "${DESTDIR}/mss/repo" ]; then
    ln -sf /mnt/mss/stuff/techy-bits/git/setboxes "${DESTDIR}/mss/repo"
fi
