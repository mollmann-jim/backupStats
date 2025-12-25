#!/usr/bin/env python3

#import requests
import re
import datetime as dt
import sqlite3
from dateutil.tz import tz
import pprint
#import json
#from sys import path
#path.append('/home/jim/tools/Ecobee/')
#import pyecobee
#import time
import os
import sys
from traceback import print_exc
import argparse

debug = False

def adapt_datetime(dt):
    return dt.isoformat(sep=' ')

def convert_datetime(val):
    return dt.datetime.fromisoformat(val).replace('T', ' ')

class getData():
    def __init__(self, DBname):
        sqlite3.register_adapter(dt.datetime, adapt_datetime)
        sqlite3.register_converter("DATETIME", convert_datetime)
        self.db             = sqlite3.connect(DBname, detect_types=sqlite3.PARSE_DECLTYPES)
        #db.set_trace_callback(print)
        self.db.row_factory = sqlite3.Row
        self.c              = self.db.cursor()
        self.table          = 'backupStats'

    def getHosts(self):
        select = 'SELECT DISTINCT host FROM ' + self.table +' ;'
        self.c.execute(select)
        result = self.c.fetchall()
        hosts  = [row[0] for row in result]
        #print('hosts:', hosts)
        return hosts

    def getBackupsByHost(self, host):
        select = 'SELECT DISTINCT  backupName FROM ' + self.table + \
            ' WHERE host IS "' + host + '" GROUP BY backupName'   + \
            ' ORDER BY backupName ; '
        #print(select)
        self.c.execute(select)
        result = self.c.fetchall()
        backups  = [row[0] for row in result]
        #print('backups:', backups)
        return backups

    def getRows(self, host, backup):
        select = 'SELECT timestamp, files, regular, totalSize,'          + \
            ' bytesSent, elapsed FROM ' + self.table                     + \
            ' WHERE host IS "' + host + '" AND backupName IS "' +  \
            backup + '" ORDER BY timestamp ; '
        print(select)
        self.c.execute(select)
        result = self.c.fetchall()
        return result

def prtHostHdr(host):
    hdr = host + ' '
    hdr = hdr + '=' * (75 - len(hdr))
    print('\n\n' + hdr)

def prtBackupHdr(host, backup):
    hdr = '  ' + host + '  ' + backup + ' '
    hdr = hdr + '-' * (75 - len(hdr))
    print('\n' + hdr)
        
        
def main():
    home     = os.getenv('HOME')
    backupDB = home + '/tools//backupStats/backups.sql'
    DB       = getData(backupDB)

    hosts    = DB.getHosts()
    for host in hosts:
        prtHostHdr(host)
        backups = DB.getBackupsByHost(host)
        #print('host:', host, 'backups:', backups)
        for backup in backups:
            backup = 'jim4'
            rows   = DB.getRows(host, backup)
            for row in rows:
                print(row['timestamp'], row['files'], row['regular'],     \
                      row['totalSize'], row['bytesSent'], row['elapsed'])
            z = timestamp / 0
                      
            prtBackupHdr(host, backup)


if __name__ == '__main__':
    # want unbuffered stdout for use with "tee"
    main()


