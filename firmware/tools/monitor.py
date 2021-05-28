#!/usr/bin/python3

import sys
import serial
import getopt
import logging

from typing import Union

def main(argv) -> None:
    serial_port:Union[str, None] = None
    try:
        opts, _ = getopt.getopt(argv, "p:", ["port="])
    except getopt.GetoptError:
        logging.exception("./monitor.py -p $SERIAL_PORT")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--port"):
            serial_port = arg
    try:
        monitor = serial.Serial(
            port=serial_port,
            baudrate=9600,
            timeout=10
        )
    except serial.SerialException as exc:
        logging.exception("Failed to initialize arduino serial monitor\n%s", exc)
        sys.exit(1)
    logging.info("Initialized arduino serial monitor on port %s", serial_port)
    while True:
        try:
            logging.info(monitor.readline())
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
    main(sys.argv[1:])