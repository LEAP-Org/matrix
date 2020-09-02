# -*- coding: utf-8 -*- 
"""
LEAP™ Transmission Control Unit
===============================
Contributors: Christian Sargusingh
Date: 2020-03-18
Repository: https://github.com/cSDes1gn/LEAP/tree/master/src/tcs
README available in repository root
Version: 3.0
 
The Transmission Control Unit is the main module for coordinating transmission events and validating
receiver connections. It extends operation to `file_parser`, `register`, and `spatial_codec` modules
The TCU is initialized with transmission files within its designated directory. It is the server for
these files and is responsible for deconstructing the file into bits, validating receiver
connections, generating custom sessions for each user request, encoding frame data to the
transmitter and scheduling transmission events.
 
Dependencies:
-------------
>>> import binascii
>>> import math
>>> import pickle
>>> import random
>>> import socket
>>> import sys
>>> import time
>>> from threading import Thread
 
>>> import numpy as np
>>> import serial
>>> import tabulate
>>> import threading_sched as sched
>>> from bitarray import bitarray
 
>>> import file_parser as parser
>>> import register as reg
>>> import spatial_codec as sc
 
 
Copyright © 2020 LEAP. All Rights Reserved.
"""
import binascii
import logging.config
import math
import random
import sys
import time
import threading

import numpy as np
import serial
import tabulate
import threading_sched as sched
from bitarray import bitarray

from tcs.codec.cache import TransmissionCache
from tcs.tcu.registry import APRegistry
from tcs.file.file_parser import FileParser

from tcs.event.registry import EventRegistry
 
class constants:
    """Transmission control unit constants class"""
    # Corresponds to baud rate defined in transmitter.ino setup()
    BAUD_RATE = 9600
    # ratio defining the capture window time allotted for the transmitter to yield a frame write
    CW_RESPONSE_RATIO = 0.95
 

class TransmissionControlUnit:
    """Class `TransmissionControlUnit` (TCU) provides the fundamental transmission control
    sequencing and interfacing between all modules within the TCS package. On initialization the TCU
    parses all transmission files boots the arduino microcontroller by initializing the `pyserial` 
    object, instantiates `Cache`, `SpatialCodec`, `socket`, `ReceiverRegister` and scaled 
    transmission scheduler objects. User parameters are validated and raise the appropriate
    exception otherwise. Upon startup TCU launches 2 primary threads. First, the access point 
    listener thread `apl_thread` listens over the `socket` for a connection request at a well-known
    port and IP address. Second, the scaled scheduler thread `sched_thread` prints random frame data
    while the scheduler has an empty queue. When transmission events are scheduled it executes them
    with precedence at the requested time.
 
    When a receiver connects it wakes the `apl_thread` and receives an APR validation key from the 
    client for validation. The TCU calls the `Cache` to validate the APR key against its contents.
    In the event of a match to an access point the `apl_thread` provides the files on the
    transmitter over the socket for the user to choose from. The file selections are sent back over
    the socket and a custom `SessionQueue` object with the frame list is instantiated by 
    `ReceiverRegister` class instance `rec_reg` and stored in the corresponding access point index. 
    Next the `transmission_scheduler()` function is called to schedule transmission events with the
    sequential frame data at times determined by a time-division multiplexing algorithm. The 
    scheduler calls function `transmit()` which uses `Cache` to cache its frame and encode the frame
    for transmission. The encoded frame data is sent serially to the arduino microcontroller. This
    is repeated until transmission scheduler is empty and the final frame is sent to the receiver
    and termination is notified by detection of a null-byte.
 
    If during transmission another receiver wakes the apl_thread with an APR validation key
    (discovered from transmission data encoded for its access point) then the process remains the
    same except that the transmission scheduler will schedule the second receivers frames
    interleaved with that of the first. This is done to maintain a constant transmission frequency
    between both receivers.
 
    Attributes:
     - `cube_dim` (`int`): transmitter cube dimension
     - `transmit_freq` (`int`): transmitter base frequency in Hz
     - `port` (`int`): well-known port for `socket` connection
     - `transmitter_port` (`str`): serial port connected to arduino microcontroller
     - `debug` (`bool`): toggle for debug mode
     - `soc` (`Socket`): socket object for remote communication with receiver via wireless network.
     - `host` (`str`): transmitter host IP address as given by wireless server.
     - `file_list` (`list`): list of file names as provided in designated files directory
     - `frame_cnt` (`int`): frame counts of each file as represented by index in `file_list`
     - `_file_data` (`list`): binary frame divided data dump of all files designated in files dir
     - `cache` (`Cache`): reference for `Cache` object
     - `rec_reg` (`ReceiverRegister`): reference for singleton`ReceiverRegister` object
     - `ser` (`Serial`): reference for `Serial` object connecting arduino microcontroller
     - `sch` (`scaled_scheduler`): reference for transmitter thread safe `scaled_scheduler` object
     - `sched_thread` (`Thread`): scheduler daemon thread instantiation
     - `apl_thread` (`Thread`): access point listener daemon thread instantiation
    
    Raises:
     - `ValueError`: for invalid input parameters for cube_dim, port, and transmit_freq 
     - `OSError`: for failure to parse files under transmission files directory.s
     - `RuntimeError`: for `socket` `ConnectionError` or duplicate instantiation of 
     `ReceiverRegister` object
     - `IOError`: for `Serial.SerialException` raise by arduino serial monitor
    """
 
    def __init__(self, init_params):
        
        self.log = logging.getLogger(__name__)

        # Data type field initialization
        self.cube_dim = 0
        self.transmit_freq = 0
        self.port = 0
        self.transmitter_port = init_params[4]
        self.debug = init_params[5]
        self.host = init_params[2]
        self.file_list = list()
        self.frame_cnt = list()
        self._file_data = list()

        # event registration
        with EventRegistry() as event:
            event.register('SHUTDOWN', self.shutdown)
 
        # Custom object field initializations
        self.cache = None
        self.rec_reg = None
        self.ser = None
        # define sched object from the threading_sched thread safe module implementation
        self.sch = sched.scaled_scheduler(time.time, time.sleep)
 
        # Threading initializations
        # daemon threads declared for simultaneous shutdown of all threads
        # self.sched_thread = Thread(target=self.scheduler,daemon=True)
 
        # Validate type matching for parameters
        try:
            cube_dim = int(init_params[0])
            transmit_freq = int(init_params[1])
            port = int(init_params[3])
        except ValueError as exc:
            self.log.exception(
                "TCU initialization failed. Dimension, frequency, and port number must be ints.")
            self.log.exception(exc)
            raise ValueError from exc
        
        # Validate cube dimension is a power of 2 and is non-negative
        if cube_dim > 0 and math.ceil(np.log2(cube_dim)) == np.log2(cube_dim):
            self.cube_dim = cube_dim
            # init spatial codec for cache _map definition
            self.cache = TransmissionCache(self.cube_dim)
        else:
            self.log.error("""TCU initialization failed. TCU initialization failed. LEAP™ only 
                supports dimensions which are powers of 2.""")
            raise ValueError
 
        # Validate frequency values are in the allowable range
        if 0 < transmit_freq <= 480:
            self.transmit_freq = 1/transmit_freq # convert to seconds
        else:
            self.log.error(
                "TCU initialization failed. LEAP™ supports frequencies between 1Hz and 480Hz.")
            raise ValueError
 
        self.log.info("Transmission frame intervals set to : %s s", self.transmit_freq)
        
        # Validate port number
        if 0 < port <= 65535:
            self.port = port
        else:
            self.log.error(
                "TCU initialization failed. Specify a valid port number (0 - 65535)")
            raise ValueError

        # initialize arduino serial connection
        try:
            self.ser = serial.Serial(self.transmitter_port,
                                     constants.BAUD_RATE, 
                                     write_timeout=(self.transmit_freq*constants.CW_RESPONSE_RATIO))
        except serial.serialutil.SerialException as exc:
            self.log.exception(
                "TCU initialization failed. Unable to establish serial connection at port: %s.",
                self.transmitter_port)
            raise IOError from exc # for clarity
        else:
            self.log.info("Transmitter serial connection successfully established.") 
        self.log.info("%s successfully instantiated", __name__)
    
    def start(self):
        """Starts transmission scheduler and access point listener thread. Diverts `main` to
        console input listener for server shutdown request.
        """
        self.scheduler()
 
    def shutdown(self):
        """
        ISR bound to SHUTDOWN
        """
        self.log.info("Purging event queue...")
        self.kill_all()
        self.log.info("done")
        self.log.info("Exiting...")
        sys.exit()

    def scheduler(self):
        """This function schedules transmission events with random frame data while the queue is
        empty. Otherwise the queued transmission events are executed in LIFO order.
        """
        while True:
            if self.sch.empty():
                self.log.info("No scheduled jobs detected. Entering idle state")
                bits = bitarray()
                # generate random 7B bitarrays
                for _ in range(pow(self.cube_dim,3)):
                    bits.append(bool(random.getrandbits(1)))
                self.sch.enter(self.transmit_freq, 4, self.transmit, argument=(0, bits), kwargs={})
            else:
                try:
                    self.log.info("Scheduled jobs detected. Serving through scheduler runner")
                    self.sch.run()
                except IOError as exc:
                    self.log.exception("""Scheduler runner encountered an error while executing the 
                    top level event: %s""", exc)
                    sys.exit(1) # exit with status code 1
 
    def transmission_scheduler(self, ap_index:int):
        """This function implements the transmitter scheduler policy which provides time-division
        multiplexing capabilities between a max of 2 concurrent users. The `SessionQueue` frames and
        corresponding transmission times are precalculated and sequenced in order to add the events
        to the scheduler in a manner that minimizes overhead between timing of event scheduling.
 
        Args:
         - `ap_index` (`int`): access point registered by connected receiver
        """
        sched_load = False
        next_transmission_time = 0
        current_sq = self.rec_reg.read()[ap_index]
 
        for i in range(len(self.sch.queue)):
            if self.sch.queue[i][1] == 4:
                sched_load = True
                next_transmission_time = self.sch.queue[i][0]
                break
 
        sched_args = list()
        time_deadlines = list()
 
        if sched_load:
            time_sum = next_transmission_time + self.transmit_freq/2  
        else:
            time_sum = time.time()
 
        #prebuild a list of transmission events and times for efficient entry into the scheduler
        while True:
            # delay added at start to avoid race between transmit() trying to read from the queue 
            # and the scheduler filling the queue
            time_sum += self.transmit_freq
            try:
                # session queue of type bitarray
                sched_args.append(current_sq.next())
            # delete session queue object when the full queue is added to the scheduler
            except ValueError:
                # disconnect signal for transmit
                time_deadlines.append(time_sum)
                sched_args.append(None)
                break
            time_deadlines.append(time_sum)
        
        #enter transmission events into the scheduler
        for i in enumerate(time_deadlines):
            self.sch.enterabs(time_deadlines[i], 4, self.transmit, 
                              argument=(ap_index,sched_args[i]), kwargs={})
        #print_queue(self.s.queue)
        self.log.info("Scheduled transmission events for AP: %s", ap_index)
        self.log.info("Estimated transmission duration (s): %s", 
            self.sch.queue[len(self.sch.queue)-1][0]-self.sch.queue[0][0])

    # TODO: ConsoleHandler for debug messages
    def transmit(self, ap_index, bin_frame):
        """This function encodes binary frame data, adds decoded frames from all access points to 
        cache and converts it to a binary hardware mapping corresponding with arduino hardware map
        as specified by `constants` class. Once the data is encoded it is sent over the serial
        connection.
 
        Args:
         - `ap_index` (`int`): access point to transmit to
         - `bin_frame` (`bitarray`): binary frame data to be transmitted
        
        Raises:
         - `IOError`: if during a `Serial.SerialTimeoutException` exception handle a 
         `Serial.SerialException` is raised.
        """
        if self.debug:
            input("\nDEBUG MESSAGE: Press enter for next frame")
 
        # disconnect handle
        if bin_frame is None:
            # delete `SessionQueue` instance from `ReceiverRegister`
            self.rec_reg.write(ap_index)
        else:
            hex_code = binascii.hexlify(bin_frame.tobytes())
            hardware_encode = self.cache.cache_map(bin_frame,ap_index)
            transmit_hex = binascii.hexlify(hardware_encode.tobytes())
            print(str(hex_code) + " | To Access Point " + str(ap_index), end='\r')
            if self.debug:
                # TODO: Move these prints to cache logger
                self.log.debug("Binary Frame Data: %s", bin_frame)
                self.log.debug("Hardware Mapping: %s", hardware_encode)
                self.log.debug("Decode from AP0: %s", self.cache._cache[-1][0])
                self.log.debug("Decode from AP1: %s", self.cache._cache[-1][1])
                self.log.debug("Decode from AP2: %s", self.cache._cache[-1][2])
                self.log.debug("Decode from AP3: %s", self.cache._cache[-1][3])

            try:
                self.ser.write(transmit_hex)
            # Purge scheduler and reboot transmitter
            except serial.SerialTimeoutException as exc:
                self.log.exception("Frame write to transmitter timed out: %s", exc)
                
    def kill_all(self):
        """
        Cancels all scheduled events in the scheduler.
        """
        #cancel all events in queue and raise RuntimeError if unsuccessful
        for event in self.sch.queue:
            try:
                self.sch.cancel(event[0])
            except RuntimeError:
                self.log.exception("Error killing top level event: %s", self.sch.queue[0])
        #Print success if no RuntimeError
        if self.sch.empty():
            self.log.info("Successfully killed all events")

@staticmethod
def print_queue(queue):
    """Prints the scheduler queue to the console using the 'tabulate' library
    """
    print(tabulate.tabulate(queue,headers=['Time','Priority','Action','Argument','kwargs'],
                            floatfmt=(".12f")))
