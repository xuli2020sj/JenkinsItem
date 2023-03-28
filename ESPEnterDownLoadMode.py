# -*- coding: utf-8 -*-  
import serial
import serial.tools.list_ports
import time
import sys
import os
import argparse


def main(argv=None):
    print("Start!")
    serial_number = ""

    parser = argparse.ArgumentParser(description='elrs_tx_test.py Factory Test Utility')
    parser.add_argument("-s", "--serial", type=str, help="serial number")
    args = parser.parse_args()

    if args.serial is None:
        print("TestResult: None input serial number!")
        exit(1)

    serial_number = args.serial
    elrs_tx_serial = serial.Serial(serial_number, 115200, timeout=5)

    elrs_tx_serial.flushInput()

    elrs_tx_serial.setDTR(False)  # IO0=HIGH
    elrs_tx_serial.setRTS(True)  # EN=LOW, chip in reset
    time.sleep(0.1)
    elrs_tx_serial.setDTR(True)  # IO0=LOW
    elrs_tx_serial.setRTS(False)  # EN=HIGH, chip out of reset
    # time.sleep(7)
    # elrs_tx_serial.setDTR(False)  # IO0=HIGH, done
    print("Done!")
    elrs_tx_serial.close()

    exit(0)


if __name__ == '__main__':
    main()
