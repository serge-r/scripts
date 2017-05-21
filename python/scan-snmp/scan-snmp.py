"""
 Scan network via fping and SNMP
 ver. 1.1
 Write html file "Report.html"

 Needs Python 3.6 jinja2, netaddr, pysnmp, multiprocess

"""

from jinja2 import Environment, FileSystemLoader
from pysnmp.hlapi import *
from datetime import datetime
import os
import netaddr as na
import time
import re
import multiprocessing as mp

# MGMT network addresses
mgmtNetwork = list(na.iter_iprange("192.168.248.1","192.168.255.254"))

# Community string
community = "public"

switches = []

# Init Template
curr_dir = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader = FileSystemLoader(curr_dir))
template = env.get_template('template.j2')

# Current time
start = time.time()
keys = ['descr','location','name','ip']

for ip in mgmtNetwork:
    if (os.system("fping " +str(ip) +" -r0 -t10 1>/dev/null") == 0):

        # for debug
        print(str(ip))

        # SNMP Vars
        errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((str(ip), 161),timeout=1,retries=0),
                    ContextData(),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)))
                   # ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises.171.12.1.1.12', 0)))
        )

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                 errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            values = [re.sub(r'\s+',' ',str(val[1])) for val in varBinds]
            values.append(str(ip))
            switch = {key:val for key,val in zip(keys,values)}
            switches.append(switch)

# Print models only
all_models = [switch['descr'] for switch in switches]
unique_models = list(set(all_models))
models_dict = []

for model in unique_models:
    models_dict.append({'name':model, 'count':all_models.count(model)})

print(models_dict)
with open("report.html",'w') as report:
    time_now = str(datetime.now())
    report.write(template.render(sw = switches,
                                 models=models_dict,
                                 time=time_now,
                                 count=len(all_models)))
    print("File writed")

print("Elasped time: {:.4f}".format(time.time() - start))
