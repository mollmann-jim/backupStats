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
import argparse

debug = False


class saveData():
    def __init__(self):
        DBname = 'backups.sql'
        self.DB = sqlite3.connect(DBname)
        self.DB.row_factory = sqlite3.Row
        self.table = 'backupStats'
        self.c = None
        self.initDB()
        #self.DB.set_trace_callback(print)
        
    def initDB(self):
        global debug
        self.c = self.DB.cursor()
        indexName = 'Nameindex'
        
        drop = 'DROP INDEX IF EXISTS ' + indexName + ';'
        if debug: print('Dropping index ', indexName)
        if debug: self.c.execute(drop)
        drop = 'DROP TABLE IF EXISTS ' + self.table + ';'
        if debug: print('Dropping table ', self.table)
        if debug: self.c.execute(drop)
        
        create = 'CREATE TABLE IF NOT EXISTS ' + self.table + ' ( \n' \
            ' recordID        INTEGER PRIMARY KEY, \n' \
            ' timestamp       INTEGER DEFAULT CURRENT_TIMESTAMP, \n' \
            ' backupName      TEXT,    \n' \
            ' files           INTEGER, \n' \
            ' created         INTEGER, \n' \
            ' deleted         INTEGER, \n' \
            ' regular         INTEGER, \n' \
            ' totalSize       INTEGER, \n' \
            ' transferredSize INTEGER, \n' \
            ' literalSize     INTEGER, \n' \
            ' bytesSent       INTEGER, \n' \
            ' bytesRcvd       INTEGER, \n' \
            ' elapsed         INTEGER  \n' \
            ' );'
        if debug: print(create)
        self.c.execute(create)
        index  = 'CREATE INDEX IF NOT EXISTS ' + indexName +\
            ' ON ' + self.table + ' (backupName);'
        if debug: print(index)
        self.c.execute(index)

    def save(self, backupName, myTime, fields):
        insert = 'INSERT INTO ' + self.table + ' (                    \n' \
            'timestamp, backupName, files, created, deleted, regular, \n' \
            'totalSize, transferredSize, literalSize, bytesSent,      \n' \
            'bytesRcvd, elapsed )                                     \n' \
            'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        myValues = [myTime] + [backupName] + fields
        print(myValues)
        values = tuple(myValues)
        print(values)
        self.c.execute(insert, values)
        
def readData(filename):
    myDate = ''
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            myData= file.read()

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return myData

def parseData(myData):
    regex = r'Start time: ([0-9:.-]+).+Epoch: ([0-9]+)\n[\S\s]+Number of files: ([0-9,]+).+\nNumber of created files: ([0-9,]+).+\nNumber of deleted files: ([0-9,]+).+\nNumber of regular files transferred: ([0-9,]+)\nTotal file size: ([0-9,]+).+\nTotal transferred file size: ([0-9,]+).+\nLiteral data: ([0-9,]+).+[\S\s]+Total bytes sent: ([0-9,]+)\nTotal bytes received: ([0-9,]+).+[\S\s]+make_snapshot.bash took ([0-9,]+)'
    
    subregex = [r'Start time: ([0-9:.-]+)',
                r'Epoch: ([0-9]+)',
                r'Number of files: ([0-9,]+)',
                r'Number of created files: ([0-9,]+)',
                r'Number of deleted files: ([0-9,]+)',
                r'Number of regular files transferred: ([0-9,]+)',
                r'Total file size: ([0-9,]+)',
                r'Total transferred file size: ([0-9,]+)',
                r'Literal data: ([0-9,]+)',
                r'Total bytes sent: ([0-9,]+)',
                r'Total bytes received: ([0-9,]+)',
                r'make_snapshot.bash took ([0-9,]+)' ]
    fields   = [None,] * 12
    try:
        countRegex = re.compile(regex)
        countMatch = countRegex.search(myData)
        print(countMatch.groups())
        fields = list(countMatch.groups())
        print('fields:', fields)
    except Exception as e:
        # Print a custom message and the exact error description
        print(f"parseData: An error occurred: {e}")
        for i in range(len(fields)):
            try:
                regexC    = re.compile(subregex[i])
                fields[i] = regexC.search(myData).group(1)
                print(i, subregex[i], fields[i])
            except:
                fields[i] = None
                print('Failed:', subregex[i])

    # DEBUG
    for i in range(len(fields)):
        print(i, '\t', subregex[i], '\t\t', fields[i])
        
    return fields

def getTime(fields):
    try:
        logtime = dt.datetime.strptime(fields[0], '%Y-%m-%d.%H:%M:%S')
    except Exception as e:
        print('getTime:', fields[0], "{e}")
        logtime = None
    try:
        utctime = dt.datetime.fromtimestamp(int(fields[1]), dt.timezone.utc)
    except Exception as e:
        print('getTime:', fields[1], f"{e}")
        utctime = None
    fields[0] = logtime
    fields[1] = utctime
    return fields
    

def main():
    global debug
    myParms = argparse.ArgumentParser(description = 'global parms')
    myParms.add_argument('-d', '--debug',   default=True, action='store_true',  help='enable debug')
    myParms.add_argument('backupName', help='backup name')
    myParms.add_argument('logFile', help='backup log file')
    args = myParms.parse_args()
    debug = args.debug
    if debug: print(args)
    backupName = args.backupName
    filename = args.logFile
    save = saveData()

    myData = readData(filename)
    fields = parseData(myData)
    print(fields)
    fields = getTime(fields)
    print(fields)
    save.save(backupName, fields)

    
if __name__ == '__main__':
    # want unbuffered stdout for use with "tee"
    buffered = os.getenv('PYTHONUNBUFFERED')
    if buffered is None:
        myenv = os.environ.copy()
        myenv['PYTHONUNBUFFERED'] = 'Please'
        os.execve(sys.argv[0], sys.argv, myenv)
    main()
