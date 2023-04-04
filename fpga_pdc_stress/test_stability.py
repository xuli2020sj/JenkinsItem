import logging
import re
import subprocess
import sys
from time import sleep

import pexpect
from pexpect import pxssh

import global_val
import pytest


pcInfo = {
    "fpga01": {'name': 'svc.fpgatest', 'ip': 'fpga01.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga02": {'name': 'svc.fpgatest', 'ip': 'fpga02.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga03": {'name': 'svc.fpgatest', 'ip': 'fpga03.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga04": {'name': 'svc.fpgatest', 'ip': 'fpga04.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga05": {'name': 'svc.fpgatest', 'ip': 'fpga05.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga06": {'name': 'svc.fpgatest', 'ip': 'fpga06.cixcomputing.cn', 'passwd': 'Cix@88008080'},
}

def pSSH(pinfo):
    chdPid = pxssh.pxssh(encoding='utf-8', timeout=240, codec_errors='replace')
    # only save output
    chdPid.logfile = sys.stdout
    chdPid.login(pinfo['ip'], pinfo['name'], pinfo['passwd'])
    return chdPid

def test_flashing():
    stopFlag = global_val.get_value('stopFlag')
    if stopFlag:
        pytest.exit("Program stop!")
    p = subprocess.Popen(r'~/test/commonFW/pdc_linux_console -i ~/test/commonFW/cix_flash_all.bin',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True
                         )
    logging.info('start flashing')
    p.wait()
    logging.info('flashing end')
    out = p.stdout.read()
    logging.info(out.decode("utf8"))
    pattern = re.compile('flashing image.*OK')
    result = re.search(pattern, out.decode("utf8"))
    assert result is not None


def test_auto_flashing():
    stopFlag = global_val.get_value('stopFlag')
    targetPC = global_val.get_value('targetPC')

    if stopFlag:
        pytest.exit("Program stop!")
    logging.info('start flashing {}')

    pcSSH = pSSH(pcInfo[targetPC])

    expect_list = [
        pexpect.EOF,
        pexpect.TIMEOUT,
        "fail",
        "flashing image.*OK",
        "Flashing PASS"
    ]
    ffwPath = "/home/svc.fpgatest/devops/lab_loader/commonFW/cix_flash_all.bin"

    logging.info("Flashing firmware from {}".format(ffwPath))
    # when index is 0, the job is successful
    index = 0
    sf100_list = ["fpga01", "fpga02", "fpga03SUB02"]
    logging.info("target PC is {}".format(targetPC))
    if targetPC in sf100_list:
        pcSSH.sendline("qflash.py -i " + ffwPath)
        index = pcSSH.expect(expect_list, timeout=240)
        logging.info(pcSSH.before)
    else:
        pcSSH.sendline("~/devops/lab_loader/commonFW/pdc_linux_console -i " + ffwPath)
        index = pcSSH.expect(expect_list, timeout=240)
        logging.info(pcSSH.before)
    assert index == 3 or index == 4
