"""
Transmission Control Software (TCS) for LEAP™ Tesseract
=======================================================
Updated: 2020-09
Defines entry point for the transmission software driver

Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging
import os
import math
import numpy as np #FIXME

from tcs.tcu.tcu import TransmissionControlUnit
from tcs.file.file_parser import FileParser
from tcs.codec.cache import TransmissionCache
from tcs.wap.ap_handler import ApHandler

class bcolors:
    """Class defining escape sequences for terminal color printing"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

logging.info("Validating environment ...")
if os.environ['DIM'] < 0:
    logging.error(
        "Received unexpected cube dimension size. Cube dimension must be a power of 2.")
    raise ValueError
logging.info("{} complete".format(bcolors.OKGREEN + "✓" + bcolors.ENDC))
logging.info("Starting Access Point Handler ...")
ApHandler()
logging.info("{} complete".format(bcolors.OKGREEN + "✓" + bcolors.ENDC))
logging.info("Starting File Parser ...")
FileParser()
logging.info("{} complete".format(bcolors.OKGREEN + "✓" + bcolors.ENDC))
logging.info("Starting Transmission Cache ...")
TransmissionCache()
logging.info("{} complete".format(bcolors.OKGREEN + "✓" + bcolors.ENDC))
logging.info("Starting Transmission Control Unit ...")
TransmissionControlUnit()
