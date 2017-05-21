"""
 Scan network via fping and SNMP
 ver. 1.1
 Write html file "Report.html"

 Needs Python 3.6 jinja2, netaddr, pysnmp, multiprocess

"""

from jinja2 import Environment, FileSystemLoader
from pysnmp.hlapi import *
from datetime import datetime
import multiprocessing as mp
import netaddr as na
import os
import time
import re

# How many start worker processess
PROC_NUMBER = 4

def divideList(list,k=2):
    lenght = len(list)
    step = math.ceil(lenght/k)
    i,j = (0,0)
    result = []
 
    for count in range(0,k):
        j = step+j
        result.append(list[i:j])
        i = j
 
    return result

def devProcess(ipList, sharedList):
    print("Process started")

    for ip in ipList:
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
                sharedList.append(switch)

    print("Process stop")

def writeTemplate(template, fileName):
    with open(FileName,'w') as report:
        time_now = str(datetime.now())
        report.write(template.render(sw = switches,
                                     models=models_dict,
                                     time=time_now,
                                     count=len(all_models)))
        print("File writed")

def main():
    """
    Executing from here
    """
    # Current time
    start = time.time()

    # Cations
    keys = ['descr','location','name','ip']

    # MGMT network addresses
    e

    # Community string
    community = "public"

    # Init Template
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader = FileSystemLoader(curr_dir))
    template = env.get_template('template.j2')

    # Working with processess
    with mp.Manager() as manager:

        switches = manager.list()

        for region in divideList(list(mgmtNetwork),PROC_NUMBER):

            p = mp.Process(target=devProcess, args=(region, switches))
            p.start()
            p.join()

    print("All processes work is stop")

    # Print models only - post thread running
    all_models = [switch['descr'] for switch in switches]

    unique_models = list(set(all_models))
    models_dict = []

    for model in unique_models:
        models_dict.append({'name':model, 'count':all_models.count(model)})

    writeTemplate(template,"Report.html")

    print("Elasped time: {:.4f}".format(time.time() - start))

# Start from here
if __name__ == '__main__':
        main()

