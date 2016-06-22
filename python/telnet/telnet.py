#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
 
Massive configuration via Telnet 

"""
# Import section
# Allowed Telnet connection
import telnetlib
# For OS imports
import os
# System
import sys
# For easy create table
from html import HTML
# For ip mgmt
from netaddr import *
# For pause
import time

# Port for telnet
PORT = 23

# Timeout - 10 sec
TIMEOUT = 10

# WaitTime - interval between commands, sec
waitTime = 2

# MGMT network addresses
mgmtNetwork = list (iter_iprange("192.168.0.3","192.168.0.254"))

# Command file
cmdFile = 'cmd.txt'

# Report File
reportFile = 'report-telnet.html'

# Results of telnet
result = {}

for ip in mgmtNetwork:
    print ("Processing ip {0}: ".format(str(ip)))
    # If conection error - catch exception Timeout
    try:
        tn = telnetlib.Telnet(str(ip),PORT,TIMEOUT)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        result[str(ip)] = "Connect Fail: {0}".format(sys.exc_info()[0])
        continue
    
    # Read commands from cmd file
    with open(cmdFile,"r") as cmd :
        for line in cmd:
             print ("Send: {0} ".format(str(line)))
            tn.write(line)
            time.sleep(waitTime)
        log = tn.read_very_eager()
        tn.close()
        # Write result as log
        result[str(ip)] = "OK: log:\n" + log 

with open(reportFile,'w') as report:
    # init HTML operations
    h = HTML ()
    report.writelines("<!DOCTYPE html>")
    report.writelines("<html>")
    report.writelines("\t<head><title>REPORT</title></head>")
    report.writelines("\t<body>")
    table = h.table(border='1')
    r = table.tr
    r.td("IP")
    r.td("Result")
    for ip,log in result.items():
        r = table.tr 
        r.td(str(ip))
        r.td(str(log))
    report.writelines(table)
    report.writelines("\t</body>")
    report.writelines("</html") 

print "Finished"

 
