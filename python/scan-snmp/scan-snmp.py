#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Scan network via fping and SNMP
 ver. 1.0
 Write html file "Report.html"

 Needs Python 2.7, html, netaddr, netsnmp libs

"""

"""
Import section

"""
# SNMP
import netsnmp

# Forf ping
import os

# For easy create table
from html import HTML

# For ip mgmt
from netaddr import *

# For test elasped time
import time

# MGMT network addresses
mgmtNetwork = list(iter_iprange("192.168.0.1","192.168.0.254"))

# Report filename
reportFile = "report.html"

# Community string
community = "public"

# SNMP Vars
#snmpVarSerial = netsnmp.Varbind('SNMPv2-SMI::enterprises.171.12.1.1.12.0')
snmpVarName = netsnmp.Varbind('SNMPv2-MIB::sysName.0')
snmpVarLocation = netsnmp.Varbind('SNMPv2-MIB::sysLocation.0')
snmpVarDescr = netsnmp.Varbind('SNMPv2-MIB::sysDescr.0')

# Base Counter
counter=0

# Models dict
models = {}

# init HTML operations
h = HTML()

# Open report file to write
with open(reportFile,'w') as report:
    report.writeli nes("<!DOCTYPE html>")
    report.writelines("<html>")
    report.writelines("\t<head><title>REPORT</title></head>")
    report.writelines("\t<body>")
    table = h.table(border='1')
    r = table.tr
    r.td("IP")
    r.td("Name")
    r.td("Description")
    r.td("Locarion")
    r.td("Serial")
    start = time.time()
    for ip in mgmtNetwork:
        
        if (os.system("fping " +str(ip) +" -r0 -t100 1>/dev/null") == 0):
            # for debug
            print (str(ip))

            r = table.tr
            name = netsnmp.snmpget(snmpVarName,Version=2,Timeout=5000,Retries=0,DestHost=str(ip),Community=community)
            descr = netsnmp.snmpget(snmpVarDescr,Version=2,Timeout=5000,Retries=0,DestHost=str(ip),Community=community)
            location = netsnmp.snmpget(snmpVarLocation,Version=2,Timeout=5000,Retries=0,DestHost=str(ip),Community=community)
            #  serial = netsnmp.snmpget(snmpVarSerial,Version=2,Timeout=5000,Retries=0,DestHost=str(ip),Community=community)
            r.td(str(ip))
            r.td(str(name))
            r.td(str(descr))
            r.td(str(location))
            # r.td(str(serial))
            counter +=  1
            if (descr != (None,)):
                if models.get(str(descr[0])) == None:
                    models[str(descr[0])] = 1
                else:
                     models[str(descr[0])] +=1
    r = table.tr
    r.td("<b>Summ:</b>")
    r.td("<b>"+str(counter)+"</b")
    report.writelines(table)
    report.writelines("\t</body>")
    report.writelines("</html")
    print("\nElasped time: {:.4f}".format(time.time() - start))
    print (models)
