#!/usr/bin/env python3

#import requests
import re
import datetime as dt
import sqlite3
from dateutil.tz import tz
import pprint
#import json
from sys import path
import os
from traceback import print_exc
import argparse

home = os.getenv('HOME')
path.append(home + '/tools/')
from shared import getTimeInterval

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
        #self.db.set_trace_callback(print)
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
        #print(select)
        self.c.execute(select)
        result = self.c.fetchall()
        return result

    def getYears(self, host):
        select_min_max_yr = 'SELECT        '\
            'min(timestamp) AS min,        '\
            'max(timestamp) AS max         '\
            'FROM ' + self.table + ' '      \
            'WHERE host IS ? ;'
        #print(select_min_max_yr)
        self.c.execute(select_min_max_yr, (host,))
        minmax = self.c.fetchone()
        first  = dt.datetime.fromisoformat(minmax['min'])
        last   = dt.datetime.fromisoformat(minmax['max'])
        return first, last

    def getBackups(self, host, bName, title):
        start, end, name = getTimeInterval.getPeriod(title)
        selectFields = 'SELECT '            \
            ' date(timestamp)    AS date,  '\
            ' timestamp,'                   \
            ' files,'                       \
            ' regular,'                     \
            ' totalSize,'                   \
            ' bytesSent,'                   \
            ' elapsed'                      \
            ' FROM ' + self.table +         \
            ' WHERE timestamp >= ? AND timestamp <= ? ' \
            ' AND host IS ? '         \
            ' AND backupName IS ? '   \
            ' ORDER BY timestamp ;'
        #print(selectFields)
        self.c.execute(selectFields, (start, end, host, bName))
        result = self.c.fetchall()
        return result

    def getStats(self, host, bName, title, stat):
        start, end, name = getTimeInterval.getPeriod(title)
        selectFields = 'SELECT '                         \
            ' COUNT(timestamp) AS count,  '              \
            ' ' + stat + '(files)       AS files,'       \
            ' ' + stat + '(regular)     AS regular,'     \
            ' ' + stat + '(totalSize)   AS totalSize,'   \
            ' ' + stat + '(bytesSent)   AS bytesSent,'   \
            ' ' + stat + '(elapsed)     AS elapsed'      \
            ' FROM ' + self.table +                      \
            ' WHERE timestamp >= ? AND timestamp <= ? '  \
            ' AND host IS ? '                            \
            ' AND backupName IS ? ; '
        #print(selectFields)
        self.c.execute(selectFields, (start, end, host, bName))
        result = self.c.fetchone()
        return name, result

                       
def prtHostHdr(host):
    hdr = host + ' '
    hdr = hdr + '=' * (75 - len(hdr))
    print('\n\n' + hdr)

def prtBackupHdr(host, backup):
    hdr = '  ' + host + '  ' + backup + '  '
    print('{:-^75s}'.format(hdr))
    
        
def fmtDT(dt):
    return dt[5:16]

def fmtNum(n):
    if n is None:
        x = '.'
    elif n < 1000000:
        if isinstance(n, int):
            x = '{:8d}'.format(n)
        elif isinstance(n, float):
            # if "n" really an integer, format it as an int
            if abs(float(int(n + 0.5)) - n) < 0.005:
                return fmtNum(int(n + 0.1))
            x = '{:#8.6g}'.format(n)
        else:
            x = str(n)
    else:
        S = ['K', 'M', 'G', 'T']
        for s in S:
            n = n / 1000
            fmt = '{:#6.6g}' + s
            x = fmt.format(n)
            if len(x) <= 8:
                break
    # strip trailing '.' or trailing '.M' 
    # '123.' -> '123'; '456.M' -> '456M'
    #print('"' + x + '"',  re.match(r'.+[0-9]\.$', x), re.match('[0-9].+\.[KMGT]$', x))
    a = re.match(r'[ 0-9]+\.$', x)
    b = re.match(r'[0-9].+\.[KMGT]$', x)
    if a or b:
        x = ' ' + x.replace('.', '')
    return x

def prtSectionHeader(fmt):
    print(fmt.format('Period', 'Stat', 'Count', 'Files', 'Regular', \
                     'totSize', 'byteSent', 'Elapsed'))
def prtSectionLine(fmt, period, stat, count, row):
    print(fmt.format(period,
                     stat,
                     fmtNum(count)[-6:],
                     fmtNum(row['files']),
                     fmtNum(row['regular']),
                     fmtNum(row['totalSize']),
                     fmtNum(row['bytesSent']),
                     fmtNum(row['elapsed'])))

def make_report(DB, host):
    print('make_report:', host)
    prtHostHdr(host)
    first, last = DB.getYears(host)
    print(first, last)
    reportFmt = '{:11s} {:>6s} {:>6s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}'
    backups = DB.getBackupsByHost(host)
    byebye=False
    for backup in backups:
        prtBackupHdr(host, backup)
        prtSectionHeader(reportFmt)
        result0 = DB.getBackups(host, backup, 'Yesterday')
        result1 = DB.getBackups(host, backup, 'Today')
        for row in result0 + result1:
            prtSectionLine(reportFmt, fmtDT(row['timestamp']), '', None, row)
            byebye=True
        for stat in ['AVG', 'MIN', 'MAX']:
            period, row = DB.getStats(host, backup, 'Prev7days', stat);
            prtSectionLine(reportFmt, period, stat, row['count'], row)

        '''
        if byebye:
            x = DB / 0
        '''
        
    
def main():
    home     = os.getenv('HOME')
    backupDB = home + '/tools//backupStats/backups.sql'
    DB       = getData(backupDB)
    hosts    = DB.getHosts()
    
    for host in hosts:
        #prtHostHdr(host)
        make_report(DB, host)
    

if __name__ == '__main__':
    # want unbuffered stdout for use with "tee"
    main()


