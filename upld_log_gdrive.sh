#!/bin/bash
# simplified process that checks if mbot.log that is produced by the mbot run machine
# locally differs from that one on Google drive and if yes - upload and del old on GD.
# script would be "cron"ed 'cyclicly' :} 


running=true
cnt=0
cd ~/Documents/mbot/voc
dt=$(date +%y-%m-%d_%H:%M:%S)
zip wav_$dt.zip *.wav	#do nothing if files not found
if [ -s wav_$dt.zip ];then
 	mv *.wav old	
	while $running; do	
		# echo "file not empty"                   upload to "voc" gdrv dir
		# ~/./gdrive-linux-x64  <- - - - - - tali gdrive PATH ~~~~
		~/Downloads/./gdrive-linux-rpi upload --parent 1rP8g6zCDCAKCwIDP0hi0_6oOUWsbUy1v wav_$dt.zip  
		if grep -q "Uploaded" u.log; then	# does u.log cotains string "Uploaded"
		  rm wav_$dt.zip
		  running=false			
		fi
		sleep 10
		let cnt++
		if [ "$cnt" -gt 10 ];then
		  echo "Error: 10 attempts to UPLOAD wav_$dt.zip file to gdrive, $(date)" >> ../tmp/sh.log
		  exit
		fi
	done
    	find old/*.wav -mtime +5 -exec rm {} \;		# del files older then 5 days
fi




#________________________________________________________________________________________________________
cd ~/Documents/mbot/tmp
rm *.txt					# deleting "tmp" content
rm mbot_cur.log					# instead *.log ?
cp ../mbot.log mbot_cur.log


echo "_________________________________________________________________ $(date)" >> sh.log

# Get latest version(ID) of mbot.log file on google drive:
# https://developers.google.com/drive/api/v3/search-parameters -->goodle drv api query parms 

running=true
cnt=0
while $running; do				# try until success(forbidden/nw errors etc.)
	# ~/Downloads/./gdrive-linux-rpi  <- - - - - - raspbery pi PATH ~~~~
	# ~/./gdrive-linux-x64  <- - - - - - tali gdrive PATH ~~~~
	~/Downloads/./gdrive-linux-rpi list -m 1 --query "name contains 'mbot.log'" > last_log_dtls.txt
	sleep 10
	let cnt++
	awk 'NR==2' last_log_dtls.txt > last_log_id.txt	   #awk 'NR==2,NR==3' somefile.txt
	if [ -s last_log_id.txt ];then 		# is file not empty ?
	  running=false				# echo "file not empty"  #echo $running
	  last_log_id=`cat last_log_id.txt | awk -F " " '{print $1}'`
	fi
	if [ "$cnt" -gt 10 ];then
	  echo "Error: 10 attempts to get mbot.log ID from gdrive, $(date)" >> sh.log
	  exit
	fi
done						# echo $last_log_id


# Download mbot.log by ID:
running=true
cnt=0
while $running; do
	~/Downloads/./gdrive-linux-rpi download $last_log_id
	sleep 10
	let cnt++
	if [ -s mbot.log ];then			# is file not empty ?
	  mv mbot.log mbot_srvr.log
	  running=false			
	fi
	if [ "$cnt" -gt 10 ];then
	  echo "Error: 10 attempts to get mbot.log FILE from gdrive, $(date)" >> sh.log
	  exit
	fi
done


# mbot_cur.log, mbot_srvr.log <-------> OK
# Compare md5 chksums and is differ ==> upload!
md5_cur=`md5sum mbot_cur.log | awk -F " " '{print $1}'`
md5_srvr=`md5sum mbot_srvr.log | awk -F " " '{print $1}'`
echo $md5_cur
echo $md5_srvr

if [ "$md5_cur" == "$md5_srvr" ];then
  echo "EQUAL"
  exit
else
  echo "NOT Equak"
  mv mbot_cur.log mbot.log			#prepare filename to upload
  running=true
  cnt=0
  while $running; do
	# --parent sends to spcfc dir. get dir name? "gdrive list": gets ALL elmnts ids(dirs incl)
	~/Downloads/./gdrive-linux-rpi upload --parent 1XovHqPKmvwQDN51GkTTSb8Vduc4f4MMv mbot.log > u.log
	if grep -q "Uploaded" u.log; then	# does u.log cotains string "Uploaded"
	  running=false			
	fi
	sleep 10
  	let cnt++
	if [ "$cnt" -gt 10 ];then
	  echo "Error: 10 attempts to UPLOAD mbot.log file to gdrive, $(date)" >> sh.log
	  exit
	fi

  done
fi #[ "$md5_cur" == "$md5_srvr" ]



# Delete OLD mbot.log on server(GD) according to checked above ID:
running=true
cnt=0
while $running; do
	~/Downloads/./gdrive-linux-rpi delete $last_log_id > u.log
	if grep -q "Deleted" u.log; then	# does u.log cotains string "Deleted"
	  echo "$last_log_id  deleted from server=OK"
	  running=false			
	fi
	sleep 10
	let cnt++
	if [ "$cnt" -gt 10 ];then
	  echo "Error: 10 attempts to UPLOAD mbot.log file to gdrive, $(date)" >> sh.log
	  exit
	fi

done


