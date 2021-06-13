# -*- coding: utf-8 -*-
"""
LEAP™ Transmission Control Unit
===============================
Modified: 2021-06
 
Copyright © 2021 LEAP. All Rights Reserved.
"""
import logging
import os

import serial

from tcs.event.registry import Registry as events
from tcs.tcu.config import TCUConfig as tc


class TransmissionControlUnit:
    """
    """

    def __init__(self, port=tc.DEFAULT_PORT):
        self._log = logging.getLogger(__name__)
        # Data type field initialization
        self.port = port
        # event registration
        events.transmit.register(self.transmit)
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

    async def transmit(self, data: bytes):
        try:
            self.ser.write(data)
        # Purge scheduler and reboot transmitter
        except serial.SerialTimeoutException as exc:
            self._log.exception("Frame write to transmitter timed out: %s", exc)
        self._log.info("Successfully wrote %s to tesseract transmitter", data)
