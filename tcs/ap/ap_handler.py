# -*- coding: utf-8 -*-
"""
Access Point Handler
====================
Modified: 2021-06

Dependencies
------------
```
import logging

from tcs.ap.socket import SocketInterface
from tcs.ap.config import APConfig as ac
```
Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging

from tcs.ap.socket import SocketInterface
from tcs.ap.config import APConfig as ac


class ApHandler:

    def __init__(self, addr=ac.DEFAULT_ADDR):
        self._log = logging.getLogger(__name__)
        self.socket = SocketInterface(addr)
        # register shutdown ISR
        self._log.info("%s successfully instantiated", __name__)

    def start(self):
        self.socket.run()

    def init_connection(self):
        # Notify success
        #self.socket.post_request(ap_index, obj=True, msg="Defining session at AP: {}".format(ap_index))
        with EventRegistry() as event:
            event.execute('FETCH_PAYLOAD')

    def post_frame_count(self, framecnt: int):
        self.socket.sendFrameNumber(framecnt)

    def shutdown(self):
        self._log.info("Shutdown request received")
        self.socket.close()
        self._log.info("Shutdown access point")
