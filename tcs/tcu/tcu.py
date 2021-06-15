# -*- coding: utf-8 -*-
"""
LEAP™ Transmission Control Unit
===============================
Modified: 2021-06

Copyright © 2021 LEAP. All Rights Reserved.
"""

import serial
import asyncio
import logging
import random
from queue import Queue
from threading import Condition

from tcs.event.registry import Registry as events
from tcs.tcu.config import TCUConfig as tc
from tcs.cache.cache import FrameCache


class TransmissionControlUnit:

    def __init__(self, port=tc.DEFAULT_PORT):
        self._log = logging.getLogger(__name__)
        # Data type field initialization
        self.port = port
        self.next_condition = Condition()
        # event registration
        events.transmit.register(self.transmit)
        events.enqueue.register(self.enqueue)
        events.uplink.register(self.uplink)
        self.frame_queue: Queue[bytes] = Queue()
        # initialize arduino serial connection
        try:
            self.ser = serial.Serial(port=self.port,
                                     baudrate=tc.BAUD_RATE,
                                     write_timeout=tc.WRITE_TIMEOUT)
        except serial.SerialException as exc:
            self._log.exception(
                "TCU initialization failed. Unable to establish serial connection at port: %s.",
                self.port)
            raise IOError from exc  # for clarity
        self._log.info("%s successfully instantiated", __name__)

    async def enqueue(self, data: bytes) -> None:
        # can we iterate through bytes returning bytes and not ints?
        for i in data:
            b = i.to_bytes(1, byteorder='little')
            self.frame_queue.put(b)
        self._log.info("Queued payload: %s", data)

    async def uplink(self) -> None:
        with self.next_condition:
            self.next_condition.notify()
        self._log.info("Notified tcu runner for new frame")

    async def run(self):
        while True:
            # perform idle action if queue is empty
            if self.frame_queue.empty():
                bytestream = bytes([random.randint(0, 255)])
                await self.transmit(bytestream)
                await asyncio.sleep(tc.IDLE_SLEEP)
            else:
                # get new item from the queue
                bytestream = self.frame_queue.get()
                await self.transmit(bytestream)
                with self.next_condition:
                    self.next_condition.wait(timeout=100)

    async def transmit(self, data: bytes) -> None:
        try:
            self.ser.write(data)
        # Purge scheduler and reboot transmitter
        except serial.SerialTimeoutException as exc:
            self._log.exception("Frame write to transmitter timed out: %s", exc)
        else:
            # cache frame
            with FrameCache() as fc:
                fc.post(data)
            self._log.info("Successfully wrote %s to tesseract", data)
