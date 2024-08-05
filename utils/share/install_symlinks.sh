#!/bin/sh

mkdir "${DESTDIR}/etc"

for i in /etc/profile /etc/bash.bashrc; do
    ln -sfv /mss/share/bash-handler \
        "${DESTDIR}/${i}"
done
