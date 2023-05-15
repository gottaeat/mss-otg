#!/bin/sh
killdwm(){ kill -TERM -"$(cat /proc/`pidof dwm`/stat | awk '{print $5}')" ;}

case "$(printf "kill-dwm\nreboot\npoweroff" | dmenu -b -p "take ya pick:")" in
 poweroff) killdwm && doas -- kill -USR1 1 ;;
 reboot)   killdwm && doas -- kill -INT  1 ;;
 kill-dwm) killdwm                         ;;
esac
