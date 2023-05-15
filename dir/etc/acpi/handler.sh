#!/bin/sh
psink="@DEFAULT_SINK@"
 psrc="@DEFAULT_SOURCE@"

case "${1}" in
 # keyboard
 button/fnf1)          : ;;
 button/fnf11)         : ;;
 button/fnf9)          : ;;
 button/suspend)       : ;;
 button/wlan)          : ;;
 button/zoom)          : ;;
 video/brightnessdown) : ;;
 video/brightnessup)   : ;;

 button/screenlock)    xorgexec xtrlock                         ;;
 button/sleep)         xorgexec xtrlock &
                       [ "${2}" = "SBTN" ] && suspendtodisk yes ;;
 video/switchmode)     xorgexec setmon                          ;;
 cd/stop)              mpc -q stop                              ;;
 cd/prev)              mpc -q prev                              ;;
 cd/play)              mpc -q toggle                            ;;
 cd/next)              mpc -q next                              ;;

 # extra keys
 button/mute)          pactl set-sink-mute   "${psink}" toggle  ;;
 button/volumedown)    pactl set-sink-volume "${psink}" -5%     ;;
 button/volumeup)      pactl set-sink-volume "${psink}" +5%     ;;
 button/micmute)       pactl set-source-mute "${psrc}"  toggle  ;;
 button/vendor)        printf '%s' 'mem' > /sys/power/state     ;;

 # lid
 button/lid)
  case "${3}" in
   open)               : ;;
   close)              : ;;
  esac
 ;;

 # charger
 ac_adapter)
  case "${4}" in
   00000000)           setbright 5   && setgov powersave        ;;
   00000001)           setbright max && setgov schedutil        ;;
  esac
 ;;

 # battery
 battery)
  case "${4}" in
   00000000)           : ;;
   00000001)           : ;;
  esac
 ;;

 # headphone in
 jack/headphone)
  case "${3}" in
   plug)               : ;;
   unplug)             : ;;
 esac
 ;;

 # mic in
 jack/microphone)
  case "${3}" in
   plug)               : ;;
   unplug)             : ;;
 esac
 ;;
 *)
  printf "acpi.script: event not understood:\n${1}\n" > /dev/kmsg
 ;;
esac
