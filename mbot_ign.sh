#!/bin/bash
# script to be put onto mbot app run machine: if machine rebooted - mbot 
# should be restarted.
# crontab -e  <------- @reboot ./~/Documents/mbot/mbot_ign.sh &
# crontab -e  <------- @reboot lxterminal --command="/bin/bash --init-file ~/Documents/mbot/mbot_ign.sh"


# check running processes ran by a command "python mbot.py" will give list of
# all running processes. Becasue current "grep" check is process by itself - there
# is needed to filter out "grep" string  ==> -v
chk_run=`ps x | grep 'python mbot.py' | grep -v "grep"`	
                                                        

if test -z "$chk_run";then
  #echo 'empty, mbot is NOT running'
  cd ~/Documents/mbot
  python mbot.py
#else
#  echo $chk_run
fi

