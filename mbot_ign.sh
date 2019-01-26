#!/bin/bash
# script to be put onto mbot app run machine: if machine rebooted - mbot 
# should be restarted.
# crontab -e  <------- @reboot ./~/Documents/mbot/mbot_ign.sh &
# crontab -e  <------- @reboot lxterminal --command="/bin/bash --init-file ~/Documents/mbot/mbot_ign.sh"
#           /|\
#            |_____ rolling back to version without terminal (crontab 'refuses' to open terminal
#                   as window ==> will run at background ++> will log ~ALL TERMINAL VISUAL DATA~
#                   with '&1'~operation,
#                   no option to append ==>copy log file with timestamp attached
#
# RESTARTABILTY: cur sh can run at chk running processes and if process 'felt'(abended) 
#                ==> restart!..  need to schedule every 10 minutes(?)
# 05/25/45 

# check running processes ran by a command "python mbot.py" will give list of
# all running processes. Becasue current "grep" check is process by itself - there
# is needed to filter out "grep" string  ==> -v
chk_run=`ps x | grep 'python mbot.py' | grep -v "grep"`	
                                                        
if test -z "$chk_run";then
  cd ~/Documents/mbot  
  #dt=$(date +%s)				#echo $dt
   dt=$(date +%y-%m-%d_%H:%M:%S)
  cp mbot_ign_run.log mbot_ign_run_$dt.log
  #echo 'empty, mbot is NOT running'
  python mbot.py 2>&1 | tee mbot_ign_run.log	# suppose to lo also ABEND
#else
#  echo $chk_run
fi

