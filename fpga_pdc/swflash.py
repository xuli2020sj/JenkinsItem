#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
1. open and ssh sessions 
2. do operations
args:
arg1 - The fpga PC name like fpga01 or fpga01-sub1
arg2 - The uploaded flash fw file. It is omissible when default fw is OK.
arg3 - Whether to update the default fw using the uploaded FW.
"""
from pexpect import pxssh
import pexpect
import sys
import os
import time

# global 
pcInfo = {
    "fpga04": {'name': 'svc.fpgatest', 'ip': 'fpga04.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga05": {'name': 'svc.fpgatest', 'ip': 'fpga05.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga06": {'name': 'svc.fpgatest', 'ip': 'fpga06.cixcomputing.cn', 'passwd': 'Cix@88008080'},
}
cPath = os.path.split(os.path.realpath(__file__))[0] + "/"


# ssh login function
def pSSH(pinfo):
    chdPid = pxssh.pxssh(encoding='utf-8', timeout=5, codec_errors='replace')
    # only save output
    chdPid.logfile = sys.stdout
    chdPid.login(pinfo['ip'], pinfo['name'], pinfo['passwd'])
    return chdPid


def heid(eid):
    if eid == 0 or eid == 1:
        return 1
    else:
        return 0


# ssh basic operations
def bOP(ss, oplist):
    op, ep, to = oplist
    ss.sendline(op)
    eid = ss.expect([pexpect.EOF, pexpect.TIMEOUT] + [ep], timeout=to)
    return heid(eid)


if __name__ == "__main__":
    # get target PC arg
    tPC = sys.argv[1].split('-')[0]
    # default fw path in remote PC
    dfwPath = "/home/svc.fpgatest/devops/lab_loader/%s/dfw/cix_flash_all.bin" % (tPC)
    # temp path for uploader fw
    tfwPath = "/home/svc.fpgatest/devops/lab_loader/%s/tfw/cix_flash_all.bin" % (tPC)
    pcSSH = pSSH(pcInfo[tPC])
    ffwPath = dfwPath
    # whether to update fw
    if len(sys.argv) >= 3 and sys.argv[2] != 'null':
        os.system(cPath + "scp.py " + sys.argv[2] + " " + tfwPath)
        ffwPath = tfwPath
    if len(sys.argv) >= 4 and sys.argv[2] != 'null' and sys.argv[3] == "Yes":
        os.system(cPath + "scp.py " + sys.argv[2] + " " + dfwPath)

    # try to flash the FW
    # os.system("which pdc_linux_console")
    flList1 = ["which pdc_linux_console", "/public/eda/software/pdc/1.0.0/bin/pdc_linux_console", 10]
    rv1 = bOP(pcSSH, flList1)

    flList = ["pdc_linux_console -i " + ffwPath, "Flashing PASS", 120]
    # flList = ["pdc_linux_console", "Flashing PASS", 120]
    rv = bOP(pcSSH, flList)
    sys.exit(rv)
