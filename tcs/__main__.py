# -*- coding: utf-8 -*-
"""
Transmission Control Software (TCS) for LEAP™ Tesseract
=======================================================
Modified: 2021-06
Entry point for the transmission software driver

Copyright © 2021 LEAP. All Rights Reserved.
"""
import sys
import getopt
import logging

from tcs.tcu.tcu import TransmissionControlUnit
from tcs.ap.ap_handler import ApHandler
from tcs.__version__ import __version__


def usage() -> None:
    print("""
    LEAP™ Transmission Control Software.

    Usage:
        python3 -m tcs -s /dev/ttyUSB0 -a 127.0.0.1:65432
        python3 -m tcs --serial-port /dev/ttyUSB0 --address 127.0.0.1:65432
        python3 -m tcs --version
        python3 -m tcs --helpå

    Options:
        -h --help\t\t Show this screen.
        -v --version\t\t Show version.
        -s --serial-port\t\t Set arduino serial port
        -a --address\t\t Set server address in <HOST:PORT> format
    """)


def main(argv: list) -> None:
    port = None
    address = None
    try:
        opts, _ = getopt.getopt(argv, "s:a:h:", ["serial-port=", "address=", "help="])
    except getopt.GetoptError:
        print("command contained unexpected arguments")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-s", "--serial-port"):
            port = arg
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-v", "--version"):
            print("LEAP TCS version: {}".format(__version__))
        else:
            usage()

    _log.info("Initializing Transmission Control Unit")
    if port is None: TransmissionControlUnit()  # initialize tcu with default port
    else: TransmissionControlUnit(port)
    _log.info("Initializing Server")
    # initialize socket
    try:
        if address is None: ApHandler()  # use default address
        else: ApHandler(address)
    except ConnectionError as exc:
        _log.exception("Socket initialization encountered an exception: %s", exc)
        raise ConnectionError from exc


if __name__ == '__main__':
    _log = logging.getLogger(__name__)
    # extract args from argument vector
    main(sys.argv[1:])
