#!/bin/sh
. /etc/profile
. /mss/etc/funcs
psink="@DEFAULT_SINK@"
 psrc="@DEFAULT_SOURCE@"

xorgexec(){
 if pidof Xorg >/dev/null 2>&1
  then
   DISPLAY=:0 ${@}
  else
   aprint_fail "X is not running."
   exit 1
 fi
}

userexec(){
 sudo -u mss -- ${@}
}

case "${1}" in
 # keyboard
 button/screenlock)    xorgexec xtrlock                                 ;;
 button/sleep)         xorgexec xtrlock &
                       [ "${2}" = "SBTN" ] && suspendtodisk yes         ;;
 button/prog1)         xorgexec xtrlock &
                       printf '%s' 'mem' > /sys/power/state             ;;

 video/switchmode)     xorgexec setmon                                  ;;

 cd/stop)              mpc -q stop                                      ;;
 cd/prev)              mpc -q prev                                      ;;
 cd/play)              mpc -q toggle                                    ;;
 cd/next)              mpc -q next                                      ;;
 button/mute)          userexec pactl set-sink-mute   "${psink}" toggle ;;
 button/micmute)       userexec pactl set-source-mute "${psrc}"  toggle ;;
 button/volumedown)    userexec pactl set-sink-volume "${psink}" -5%    ;;
 button/volumeup)      userexec pactl set-sink-volume "${psink}" +5%    ;;

#video/brightnessdown) setbright -                                      ;;
#video/brightnessup)   setbright +                                      ;;

 ac_adapter)
  case "${4}" in
   00000000)           setbright 10  && setgov powersave                ;;
   00000001)           setbright max && setgov schedutil                ;;
  esac
 ;;

 button/up|button/down|button/left|button/right|button/kpenter)         ;;

 *)
  printf "acpi.script: event not understood:\n${1}\n" > /dev/kmsg
 ;;
esac
