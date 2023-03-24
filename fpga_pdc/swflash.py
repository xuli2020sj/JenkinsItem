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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', '-j', required=True, type=str)
    parser.add_argument('--firmware', '-f', required=False, type=str)
    parser.add_argument('--default', '-a', required=False, type=str)
    args = parser.parse_args()
    firmware = args.firmware
    job_list = args.job.split('_')

    targetPC = pcInfo[job_list[2].lower()]
    logging.info("Target PC is {}".format(targetPC))
    # ssh 登录
    pcSSH = pSSH(targetPC)

    # support sub
    dir_name = job_list[2]
    if len(job_list) > 3 and job_list[3] != "Admin":
        dir_name += job_list[3]
        targetPC += job_list[3]
    root_dir = "/home/svc.fpgatest/devops/lab_loader/" + dir_name

    bOP(pcSSH, ["mkdir " + root_dir, "", 3])
    default_firmware_dir = root_dir + "/default_firmware"
    temp_firmware_dir = root_dir + "/temp_firmware"
    bOP(pcSSH, ["mkdir " + default_firmware_dir, "", 3])
    bOP(pcSSH, ["mkdir " + temp_firmware_dir, "", 3])

    # whether to update fw
    if job_list.count('Admin') and args.default == "Yes" and firmware != "null":
        os.system("python3 " + cPath + "scp.py " + firmware + " " + default_firmware_dir + "/cix_flash_all.bin")

    # check default fw exists, otherwise copy default from /home/svc.fpgatest/devops/lab_loader/commonFW
    expect_list1 = [
        pexpect.EOF,
        pexpect.TIMEOUT,
        "cix_flash_all.bin"
    ]
    pcSSH.sendline("ls " + default_firmware_dir)
    id = pcSSH.expect(expect_list1, timeout=10)
    logging.info("Default FM exist.")
    if id != 2:
        logging.info("Default FM didn't exist. Copying file from commonFW")
        pcSSH.sendline("cp /home/svc.fpgatest/devops/lab_loader/commonFW/cix_flash_all.bin "
                       "/home/svc.fpgatest/devops/lab_loader/{}/default_firmware/".format(dir_name))
        pcSSH.expect(expect_list1, timeout=10)

    # whether to flash default fw
    ffwPath = default_firmware_dir + "/cix_flash_all.bin"
    if firmware == "non_default_flash_fw":
        logging.info("Flashing uploaded firmware")
        os.system("python3 " + cPath + "scp.py " + firmware + " " + temp_firmware_dir + "/cix_flash_all.bin")
        ffwPath = temp_firmware_dir + "/cix_flash_all.bin"
    else:
        logging.info("Flashing default firmware")

    expect_list = [
        pexpect.EOF,
        pexpect.TIMEOUT,
        "fail",
        "checking image.*OK",
        "Flashing PASS"
    ]

    logging.info("Flashing firmware from {}".format(ffwPath))
    # when index is 0, the job is successful
    index = 0
    sf100_list = ["fpga01", "fpga02", "fpga03SUB02"]
    if targetPC in sf100_list:
        pcSSH.sendline("qflash.py -i " + ffwPath)
        index = pcSSH.expect(expect_list, timeout=240)
    else:
        pcSSH.sendline("pdc_linux_console -i " + ffwPath)
        index = pcSSH.expect(expect_list, timeout=240)

    if index == 0 or index == 1 or index == 2:
        logging.info("Flashing failed")
        sys.exit(1)
    else:
        logging.info("Flashing succeed")
        sys.exit(0)
