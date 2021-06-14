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

from tcs.api.server import app as server
from tcs.tcu.tcu import TransmissionControlUnit
from tcs.__version__ import __version__


def usage(exit_code: int) -> None:
    print("""
    LEAP™ Transmission Control Software.

    Usage:
        python3 -m tcs -s /dev/ttyUSB0 -a 127.0.0.1:65432
        python3 -m tcs --serial-port /dev/ttyUSB0 --address 127.0.0.1:65432
        python3 -m tcs --version=
        python3 -m tcs --help=

    Options:
        -h --help\t\t Show this screen.
        -v --version\t\t Show version.
        -s --serial-port\t\t Set arduino serial port
        -a --address\t\t Set server address in <HOST:PORT> format
    """)
    sys.exit(exit_code)


def main(argv: list) -> None:
    port = None
    address = None
    opts = []
    try:
        opts, _ = getopt.getopt(argv, "s:a:h:v:", ["serial-port=", "address=", "help=", "version="])
    except getopt.GetoptError:
        print("command contained unexpected arguments")
        usage(exit_code=2)
    if opts == []: usage(exit_code=2) 
    for opt, arg in opts:
        if opt in ("-s", "--serial-port"):
            serial = arg
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-v", "--version"):
            print("LEAP TCS version: {}".format(__version__))
            sys.exit(0)
        else:
            usage(exit_code=0)

    _log.info("Initializing Transmission Control Unit")
    # if serial is None: TransmissionControlUnit()  # initialize tcu with default port
    # else: TransmissionControlUnit(serial)
    _log.info("Initializing Server")
    # initialize socket
    host, port = address.split(':')  # Port to listen on (non-privileged ports are > 1023)
    port = int(port)
    # start flask server
    server.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    _log = logging.getLogger(__name__)
    # extract args from argument vector
    main(sys.argv[1:])
