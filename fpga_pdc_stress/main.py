import argparse
import signal
import pytest
import global_val
import logging
import logging.config

pcInfo = {
    "fpga01": {'name': 'svc.fpgatest', 'ip': 'fpga01.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga02": {'name': 'svc.fpgatest', 'ip': 'fpga02.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga03": {'name': 'svc.fpgatest', 'ip': 'fpga03.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga04": {'name': 'svc.fpgatest', 'ip': 'fpga04.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga05": {'name': 'svc.fpgatest', 'ip': 'fpga05.cixcomputing.cn', 'passwd': 'Cix@88008080'},
    "fpga06": {'name': 'svc.fpgatest', 'ip': 'fpga06.cixcomputing.cn', 'passwd': 'Cix@88008080'},
}


def quit(signum, frame):
    logging.info("Test Stopping！")
    global_val.set_value('stopFlag', True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    parser = argparse.ArgumentParser()
    parser.add_argument('--count', '-c', required=False, type=int, default=10)
    parser.add_argument('--target', '-t', required=False, type=str)
    parser.add_argument('--module', '-m', required=False, type=str, default="test_auto_flashing")

    args = parser.parse_args()
    count_cmd = "--count={}".format(args.count)
    target_cmd = args.target.lower()
    test_cmd = "fpga_pdc_stress/test_stability.py::{}".format(args.module)

    global_val.init()
    global_val.set_value('stopFlag', False)
    global_val.set_value('targetPC', target_cmd)

    pytest.main(["-s", test_cmd, count_cmd, '--html=report.html', '--self-contained-html', '--capture=sys'])
