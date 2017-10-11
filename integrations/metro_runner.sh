#! /bin/bash

case "$(pidof python | wc -w)" in

0)  echo "Restarting Metro feed:        $(date)" >> /home/pi/metro.log
    python /home/pi/metro_main.py >> /home/pi/metro.log
    ;;
1)  # all ok
    ;;
*)  echo "Removed double Metro process: $(date)" >> /home/pi/metro.log
    kill $(pidof python | awk '{print $1}')
    ;;
esac
