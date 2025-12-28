#!/bin/bash
set -x
logDir="$HOME/tools/backupStats/logs/"
log=$logDir/report.$(/bin/date +%F-%T | /usr/bin/tr : .);
reportDir="$HOME/SynologyDrive/Reports.Daily/"
$HOME/tools/backupStats/reportBackup.py &>> $log
cp -p $log $reportDir/Backups.txt
cp -p $log $reportDir/All/Backups.$(basename -- "$log").txt
#cat $log
# keep only the newest
REMOVE=$(ls -t $logDir/report* | sed 1,20d)
if [ -n "$REMOVE" ]; then
    /bin/rm $REMOVE
fi
me='jim.mollmann@gmail.com'
####(echo -e "Subject: Weather Summary: $(date)\n"; cat $log) | sendmail -F $me $me

