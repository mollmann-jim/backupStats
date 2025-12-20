#!/usr/bin/env python3

#import requests
import re
import datetime as dt
import sqlite3
from dateutil.tz import tz
import pprint
import json
#from sys import path
#path.append('/home/jim/tools/Ecobee/')
#import pyecobee
import time
import os
import sys
from traceback import print_exc

log1 = '''
var/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-ModemManager.service-8VSRwl/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-ModemManager.service-8VSRwl/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-abrtd.service-f0tuCB/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-abrtd.service-f0tuCB/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-chronyd.service-W1Y1NL/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-chronyd.service-W1Y1NL/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-colord.service-JExUA6/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-colord.service-JExUA6/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-dbus-broker.service-CdKSdS/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-dbus-broker.service-CdKSdS/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-irqbalance.service-DE4gis/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-irqbalance.service-DE4gis/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-polkit.service-R5lmDe/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-polkit.service-R5lmDe/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-postfix.service-RXgU0X/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-postfix.service-RXgU0X/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-rtkit-daemon.service-a2upVQ/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-rtkit-daemon.service-a2upVQ/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-switcheroo-control.service-eBuzAC/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-switcheroo-control.service-eBuzAC/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-systemd-logind.service-OIC9Gi/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-systemd-logind.service-OIC9Gi/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-systemd-oomd.service-Rlv628/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-systemd-oomd.service-Rlv628/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-systemd-resolved.service-pMe4Bg/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-systemd-resolved.service-pMe4Bg/tmp/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-upower.service-RJhkcd/
var/tmp/systemd-private-eb219102d3424a088694f44b82c8b119-upower.service-RJhkcd/tmp/
var/www/
var/www/cgi-bin/
var/www/html/

Number of files: 1,169,590 (reg: 986,353, dir: 84,614, link: 98,593, special: 30)
Number of created files: 36,217 (reg: 29,961, dir: 4,817, link: 1,439)
Number of deleted files: 33,013 (reg: 27,015, dir: 4,614, link: 1,384)
Number of regular files transferred: 98,928
Total file size: 1,460,109,828,941 bytes
Total transferred file size: 44,797,664,785 bytes
Literal data: 44,797,665,588 bytes
Matched data: 0 bytes
File list size: 11,678,355
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 44,845,354,880
Total bytes received: 4,532,826

sent 44,845,354,880 bytes  received 4,532,826 bytes  48,096,394.32 bytes/sec
total size is 1,460,109,828,941  speedup is 32.56
rsync // /hourly.0 took 932 seconds
/bin/echo starting rm
/bin/rm -rf /backups/jim4/./hourly.6.delete
starting rm
rm took 0 seconds
wait took 0 seconds
/usr/sbin/btrfs filesystem defragment /backups/jim4
btrfs defragment /backups/jim4 took 0 seconds
/dev/sdc1 on /backups/jim4 type btrfs (rw,relatime,seclabel,compress=zstd:3,discard=async,space_cache=v2,subvolid=256,subvol=/@backup.jim4)
/root/backups/jim4/make_snapshot.bash took 2222 seconds
/root/backups/jim4/run_backups.bash took 2222 seconds
'''
log2 = '''
var/log/cron
var/log/hawkey.log
var/log/maillog
var/log/messages
var/log/secure
var/log/audit/
var/log/audit/audit.log
var/log/audit/audit.log.1
var/log/audit/audit.log.2
var/log/audit/audit.log.3
var/log/audit/audit.log.4
var/log/journal/c1d8d3a79a9947a194d6473c3193f0ae/system.journal
var/log/journal/c1d8d3a79a9947a194d6473c3193f0ae/user-1000.journal
var/log/journal/c1d8d3a79a9947a194d6473c3193f0ae/user-1007.journal
var/log/sa/sa18
var/spool/postfix/active/
var/spool/postfix/incoming/
var/spool/postfix/maildrop/

Number of files: 1,170,161 (reg: 986,922, dir: 84,615, link: 98,594, special: 30)
Number of created files: 23 (reg: 23)
Number of deleted files: 10 (reg: 10)
Number of regular files transferred: 148
Total file size: 1,458,127,519,982 bytes
Total transferred file size: 24,368,777,820 bytes
Literal data: 24,368,778,311 bytes
Matched data: 0 bytes
File list size: 6,880,224
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 24,407,234,736
Total bytes received: 93,759

sent 24,407,234,736 bytes  received 93,759 bytes  50,376,323.00 bytes/sec
total size is 1,458,127,519,982  speedup is 59.74
rsync // /hourly.0 took 484 seconds
/bin/echo starting rm
/bin/rm -rf /backups/jim4/./hourly.6.delete
starting rm
rm took 0 seconds
wait took 0 seconds
/usr/sbin/btrfs filesystem defragment /backups/jim4
btrfs defragment /backups/jim4 took 0 seconds
/dev/sdc1 on /backups/jim4 type btrfs (rw,relatime,seclabel,compress=zstd:3,discard=async,space_cache=v2,subvolid=256,subvol=/@backup.jim4)
/root/backups/jim4/make_snapshot.bash took 3267 seconds
/root/backups/jim4/run_backups.bash took 3267 seconds
'''

regex = r'Number of files: ([0-9,]+).+\nNumber of created files: ([0-9,]+).+\nNumber of deleted files: ([0-9,]+).+\nNumber of regular files transferred: ([0-9,]+)\nTotal file size: ([0-9,]+).+\nTotal transferred file size: ([0-9,]+).+\nLiteral data: ([0-9,]+).+[\S\s]+Total bytes sent: ([0-9,]+)\nTotal bytes received: ([0-9,]+)\nsent.+[\S\s]+make_snapshot.bash took ([0-9,]+)'
regex = r'Number of files: ([0-9,]+).+\nNumber of created files: ([0-9,]+).+\nNumber of deleted files: ([0-9,]+).+\nNumber of regular files transferred: ([0-9,]+)\n'
regex = r'Number of files: ([0-9,]+).+\nNumber of created files: ([0-9,]+).+\nNumber of deleted files: ([0-9,]+).+\nNumber of regular files transferred: ([0-9,]+)\nTotal file size: ([0-9,]+).+\nTotal transferred file size: ([0-9,]+).+\nLiteral data: ([0-9,]+)'
regex = r'Number of files: ([0-9,]+).+\nNumber of created files: ([0-9,]+).+\nNumber of deleted files: ([0-9,]+).+\nNumber of regular files transferred: ([0-9,]+)\nTotal file size: ([0-9,]+).+\nTotal transferred file size: ([0-9,]+).+\nLiteral data: ([0-9,]+).+[\S\s]+Total bytes sent: ([0-9,]+)\nTotal bytes received: ([0-9,]+)\n'
regex = r'Number of files: ([0-9,]+).+\nNumber of created files: ([0-9,]+).+\nNumber of deleted files: ([0-9,]+).+\nNumber of regular files transferred: ([0-9,]+)\nTotal file size: ([0-9,]+).+\nTotal transferred file size: ([0-9,]+).+\nLiteral data: ([0-9,]+).+[\S\s]+Total bytes sent: ([0-9,]+)\nTotal bytes received: ([0-9,]+).+[\S\s]+make_snapshot.bash took ([0-9,]+)'

countRegex = re.compile(regex)
countMatch = countRegex.search(log1)
print(countMatch)
print(countMatch.group(1))
print(countMatch.group(2))
print(countMatch.groups())

countMatch = countRegex.search(log2)
print(countMatch)
print(countMatch.group(1))
print(countMatch.group(2))
print(countMatch.groups())

'''
(files, created, deleted, regular, transferred, totalSize, \
 transferredSize, literal, sent, received, elapsed) = counts.search(log1).group(1, 2, 3, 4, 5, 6, 

print(files, created, deleted, regular, transferred, totalSize, \
 transferredSize, literal, sent, received, elapsed)
'''
