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

    expect_list = [
        pexpect.EOF, pexpect.TIMEOUT
    ] + [ep]
    eid = ss.expect(expect_list, timeout=to)

    return heid(eid)


def flash_fm():
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
    targetPC = pcInfo[job_list[2].lower()]

    # ssh 登录
    pcSSH = pSSH(targetPC)

    dir_name = job_list[2]
    if len(job_list) > 3 and job_list[3] != "Admin":
        dir_name += job_list[3]
    root_dir = "/home/svc.fpgatest/devops/lab_loader/" + dir_name
    default_firmware_dir = root_dir + "/default_firmware"
    temp_firmware_dir = root_dir + "/temp_firmware"

    if not os.path.exists(root_dir):
        logging.info("Dir didn't exist! Start to create dir: " + root_dir)
        bOP(pcSSH, ["mkdir " + root_dir, "", 3])
        bOP(pcSSH, ["mkdir " + default_firmware_dir, "", 3])
        bOP(pcSSH, ["mkdir " + temp_firmware_dir, "", 3])

    # whether to update fw
    if job_list.count('Admin') and args.default == "Yes":
        os.system("python3 " + cPath + "scp.py " + firmware + " " + default_firmware_dir + "/cix_flash_all.bin")

    # whether to flash default fw
    ffwPath = default_firmware_dir + "/cix_flash_all.bin"
    if os.path.exists(firmware):
        os.system("python3 " + cPath + "scp.py " + firmware + " " + temp_firmware_dir + "/cix_flash_all.bin")
        ffwPath = temp_firmware_dir + "/cix_flash_all.bin"

    expect_list = [
        pexpect.EOF,
        pexpect.TIMEOUT,
        "fail",
        "checking image.*OK"
    ]
    pcSSH.sendline("pdc_linux_console -i " + ffwPath)
    index = pcSSH.expect(expect_list, timeout=240)
    if index == 0 or index == 1 or index == 2:
        sys.exit(1)
    else:
        sys.exit(0)
