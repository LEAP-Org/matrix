"""
Transmission Control Software (TCS)
===================================

Defines entry point for the transmission software driver

Copyright © 2020 LEAP. All Rights Reserved.
"""
import os
import sys

from tcs.controller.tcu import TransmissionControlUnit
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

def user_prompt():
    """Prompt TCU object initialization parameters.
    """
    input("Press any key to begin transmitter initialization.")
    print("Press enter for default values.")
    
    # list of params for tcu to process and validate
    params = list()
 
    cube_dim = input("Enter the LED Cube dimension: ")
    #default to 4
    if cube_dim == '':
        cube_dim = '4'
        print("Cube dimensions: " + bcolors.OKGREEN + cube_dim + bcolors.ENDC)
    else:
        print("Cube dimensions: " + bcolors.OKGREEN + cube_dim + bcolors.ENDC)
    # append cube dim to parameter 
    params.append(cube_dim)
    
    transmit_freq = input("Base transmission frequency (Hz/FPS): ")
    #default to 30 Hz
    if transmit_freq == '':
        transmit_freq = '30'
        print("Transmission Frequency (Hz): " + bcolors.OKGREEN + transmit_freq + bcolors.ENDC)
    else:
        print("Transmission Frequency (Hz): " + bcolors.OKGREEN + transmit_freq + bcolors.ENDC)
    # append transmit frequency to parameter list
    params.append(transmit_freq)
    
    host = input("Enter a host IP: ")
    if host == '':
        host = 'localhost'
        print("Host: " + bcolors.OKGREEN + host + bcolors.ENDC)
    else:
        print("Host: " + bcolors.OKGREEN + host + bcolors.ENDC)
    # append host to parameter list
    params.append(host)
 
    port = input("Enter a port: ")
    #default to port 65432
    if port == '':
        port = '65432'
        print("Port: " + bcolors.OKGREEN + port + bcolors.ENDC)
    else:
        print("Port: " + bcolors.OKGREEN + port + bcolors.ENDC)
    # append host to parameter list
    params.append(port)
 
    transmitter_port = input("Enter transmitter serial port: ")
    #default to linux IO port /dev/ttyS5
    if transmitter_port == '':
        transmitter_port = '/dev/ttyUSB0'
        print("Transmitter Port: " + bcolors.OKGREEN + transmitter_port + bcolors.ENDC)
    else:
        print("Transmitter Port: " + bcolors.OKGREEN + transmitter_port + bcolors.ENDC)
    # append host to parameter list
    params.append(transmitter_port)
    
    debug = bool(input("Debug Mode?: "))
    # append host to parameter list
    params.append(debug)
    return params

# Threading initializations
# daemon threads declared for simultaneous shutdown of all threads
ap_handler = ApHandler(os.environ.get('HOSTNAME'))

try:
    self.ap_thread.start()
except RuntimeError as exc:
    self.log.critical("Access Point Handler initialization encountered an error: %s", exc)
    sys.exit(1) # exit with status code 1
else:
    self.log.info("Access Point Listener thread initialization successful.")

# get parameters from environment
try:
    TCU = TransmissionControlUnit(
        [int(os.environ.get('DIM')),
         int(os.environ.get('T_FREQ')),
         os.environ.get('HOSTNAME'),
         int(os.environ.get('PORT')),
         os.environ.get('SERIAL_PORT'),
         bool(os.environ.get('TCS_ENV'))]
    )
except (RuntimeError, ConnectionError, IOError):
    print(bcolors.FAIL + "Reboot the system and try again." + bcolors.ENDC)
    sys.exit(1)
except (ValueError):
    # clear parameter list and request new parameters from user
    print(bcolors.FAIL + "Re-input parameters for transmitter initialization." + bcolors.ENDC)
else:
    # launch TCU
    TCU.start()

