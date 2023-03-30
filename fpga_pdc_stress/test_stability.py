import logging
import re
import subprocess
from time import sleep
import global_val
import pytest


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


def test_():
    stopFlag = global_val.get_value('stopFlag')
    if stopFlag:
        pytest.exit("Program stop!")
    logging.info('start flashing {}')
    sleep(1)
    logging.info('flashing end {}')
