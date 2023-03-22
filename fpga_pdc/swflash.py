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
import logging

from pexpect import pxssh
import pexpect
import sys
import os
import argparse
import clogging

# global 
pcInfo = {
    "fpga01": {'name': 'svc.fpgatest', 'ip': 'fpga01.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga02": {'name': 'svc.fpgatest', 'ip': 'fpga02.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga03": {'name': 'svc.fpgatest', 'ip': 'fpga03.cixcomputing.cn', 'passwd': 'Cix@88008080'},
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


def flash_fm(target_pc):
    pcSSH = pSSH(target_pc)
    flList = ["pdc_linux_console -i " + ffwPath, "checking image.*OK", 240]
    return bOP(pcSSH, flList)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', '-j', required=True, type=str)
    parser.add_argument('--firmware', '-f', required=False, type=str)
    parser.add_argument('--default', '-a', required=False, type=str)
    args = parser.parse_args()
    firmware = args.firmware
    job_list = args.job.split('_')

    dir_name = job_list[2]
    if len(job_list) > 3 and job_list[3] != "Admin":
        dir_name += job_list[3]
    root_dir = "/home/svc.fpgatest/devops/lab_loader/" + dir_name
    default_firmware_dir = root_dir + "/default_firmware"
    temp_firmware_dir = root_dir + "/temp_firmware"

    if not os.path.exists(root_dir):
        logging.info("Dir didn't exist! Start to create dir " + root_dir)
        os.makedirs(root_dir)
        os.makedirs(default_firmware_dir)
        os.makedirs(temp_firmware_dir)

    # whether to update fw
    if job_list.count('Admin') and args.default == "Yes":
        os.system("python3 " + cPath + "scp.py " + firmware + " " + default_firmware_dir)

    # whether to flash default fw
    ffwPath = default_firmware_dir + "/cix_flash_all.bin"
    if os.path.exists(firmware):
        os.system("python3 " + cPath + "scp.py " + firmware + " " + temp_firmware_dir)
        ffwPath = temp_firmware_dir + "/cix_flash_all.bin"

    flash_fm(pcInfo[job_list[2]])
    sys.exit(0)
