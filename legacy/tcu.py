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
import logging
import random
import sys
import time
import os
from typing import List

import serial
import tabulate
import threading_sched as sched
from bitarray import bitarray

from tcs.codec.cache import TransmissionCache
from tcs.tcu.registry import APRegistry
from tcs.file.file_parser import FileParser
from tcs.wap.ap_handler import ApHandler

from tcs.event.registry import EventRegistry
 
class constants:
    """Transmission control unit constants class"""
    # Corresponds to baud rate defined in transmitter.ino setup()
    BAUD_RATE = 9600
    # ratio defining the capture window time allotted for the transmitter to yield a frame write
    CW_RESPONSE_RATIO = 0.95
 

class TransmissionControlUnit:
    """
    """
 
    def __init__(self):
        
        self.log = logging.getLogger(__name__)

        # Data type field initialization
        self.cube_dim = int(os.environ['DIM'])
        self.transmit_freq = int(os.environ['T_FREQ'])
        self.transmitter_port = os.environ['SERIAL_PORT']

        # event registration
        with EventRegistry() as event:
            event.register('SHUTDOWN', self.shutdown)
            event.register('TRANSMIT', self.transmit)

        # define sched object from the threading_sched thread safe module implementation
        self.sch = sched.scaled_scheduler(time.time, time.sleep)
 
        # Threading initializations
        # daemon threads declared for simultaneous shutdown of all threads
        # self.sched_thread = Thread(target=self.scheduler,daemon=True)

        self.transmit_freq = 1/self.transmit_freq # convert to seconds
        self.log.info("Transmission frame intervals set to : %s s", self.transmit_freq)

        # initialize socket
        try:
            self.ap_handler = ApHandler()
        except ConnectionError as exc:
            self.log.exception("Socket initialization encountered an exception: %s", exc)
            raise ConnectionError from exc

        # initialize arduino serial connection
        try:
            self.ser = serial.Serial(self.transmitter_port,
                                     constants.BAUD_RATE, 
                                     write_timeout=(self.transmit_freq*constants.CW_RESPONSE_RATIO))
        except serial.SerialException as exc:
            self.log.exception(
                "TCU initialization failed. Unable to establish serial connection at port: %s.",
                self.transmitter_port)
            raise IOError from exc # for clarity
        else:
            self.log.info("Transmitter serial connection successfully established.") 
        self.log.info("%s successfully instantiated", __name__)
        # selector for runtime executable
        if os.environ['TCS_ENV'] == 'demo':
            # self.demo(message="Hello my name is christian welcome to leap")
            self.debug()
        elif os.environ['TCS_ENV'] == 'server':
            self.ap_handler.run_server()
        else:
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

    def demo(self, message:str) -> None:
        """
        Transmit an ASCII encoded message
        """
        print("LEAP text encoding: {}".format(message))
        for byte in message:
            ascii_byte = bytes(byte, 'ascii')
            print("{} -> {}".format(byte, ord(byte)))
            self.ser.write(ascii_byte)
            # time.sleep(0.01)
        
    def debug(self) -> None:
        """
        Transmit list of bytestream
        """
        
        # print(bytes([3]))
        # self.ser.write(bytes([x for x in range(256)]))
        
        for byte in [[x] for x in range(256)]:
            print("Loading -> {}".format(byte))
            self.ser.write(bytes(byte))
            time.sleep(0.1)
    
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
        # sched_load = False
        # next_transmission_time = 0
        # current_sq = self.rec_reg.read()[ap_index]
 
        # for i in range(len(self.sch.queue)):
        #     if self.sch.queue[i][1] == 4:
        #         sched_load = True
        #         next_transmission_time = self.sch.queue[i][0]
        #         break
 
        # sched_args = list()
        # time_deadlines = list()
 
        # if sched_load:
        #     time_sum = next_transmission_time + self.transmit_freq/2  
        # else:
        #     time_sum = time.time()
 
        # #prebuild a list of transmission events and times for efficient entry into the scheduler
        # while True:
        #     # delay added at start to avoid race between transmit() trying to read from the queue 
        #     # and the scheduler filling the queue
        #     time_sum += self.transmit_freq
        #     try:
        #         # session queue of type bitarray
        #         sched_args.append(current_sq.next())
        #     # delete session queue object when the full queue is added to the scheduler
        #     except ValueError:
        #         # disconnect signal for transmit
        #         time_deadlines.append(time_sum)
        #         sched_args.append(None)
        #         break
        #     time_deadlines.append(time_sum)
        
        # #enter transmission events into the scheduler
        # for i in enumerate(time_deadlines):
        #     self.sch.enterabs(time_deadlines[i], 4, self.transmit, 
        #                       argument=(ap_index,sched_args[i]), kwargs={})
        # #print_queue(self.s.queue)
        # self.log.info("Scheduled transmission events for AP: %s", ap_index)
        # self.log.info("Estimated transmission duration (s): %s", 
        #     self.sch.queue[len(self.sch.queue)-1][0]-self.sch.queue[0][0])

    # TODO: ConsoleHandler for debug messages
    def transmit(self, data):
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
        # ascii_stream = bytes(data, 'ascii')
        # self.log.info('Encoding bytestream: %s to ascii: %s', data, ascii_stream)
        try:
            self.ser.write(data)
        # Purge scheduler and reboot transmitter
        except serial.SerialTimeoutException as exc:
            self.log.exception("Frame write to transmitter timed out: %s", exc)
        self.log.info("Successfully wrote %s to tesseract transmitter", data)
        # # disconnect handle
        # if bin_frame is None:
        #     # delete `SessionQueue` instance from `ReceiverRegister`
        #     self.rec_reg.write(ap_index)
        # else:
        #     hex_code = binascii.hexlify(bin_frame.tobytes())
        #     hardware_encode = self.cache.cache_map(bin_frame,ap_index)
        #     transmit_hex = binascii.hexlify(hardware_encode.tobytes())
        #     print(str(hex_code) + " | To Access Point " + str(ap_index), end='\r')
        #     if os.environ['TCS_ENV'] == 'dev':
        #         # TODO: Move these prints to cache logger
        #         self.log.debug("Binary Frame Data: %s", bin_frame)
        #         self.log.debug("Hardware Mapping: %s", hardware_encode)
        #         self.log.debug("Decode from AP0: %s", self.cache._cache[-1][0])
        #         self.log.debug("Decode from AP1: %s", self.cache._cache[-1][1])
        #         self.log.debug("Decode from AP2: %s", self.cache._cache[-1][2])
        #         self.log.debug("Decode from AP3: %s", self.cache._cache[-1][3])
                
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
