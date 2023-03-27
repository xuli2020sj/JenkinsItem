import argparse
import signal
import pytest
import global_val
import logging
import logging.config


def quit(signum, frame):
    logging.info("Test Stopping！")
    global_val.set_value('stopFlag', True)
    # pytest.exit("Test Stopping！")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)

    parser = argparse.ArgumentParser()
    parser.add_argument('--count', '-c', required=False, type=int, default=10)
    parser.add_argument('--module', '-m', required=False, type=str, default="test_")

    args = parser.parse_args()
    count_cmd = "--count={}".format(args.count)
    test_cmd = "fpga_pdc_stress/test_stability.py::{}".format(args.module)

    global_val.init()
    global_val.set_value('stopFlag', False)

    pytest.main(["-s", test_cmd, count_cmd])
