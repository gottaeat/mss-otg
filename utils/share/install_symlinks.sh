#!/bin/sh

mkdir -pv "${DESTDIR}/etc"

for i in etc/profile etc/bash.bashrc; do
    if [ ! -L "${DESTDIR}/${i}" ]; then
        ln -sfv /mss/share/bash-handler "${DESTDIR}/${i}"
    fi
done
