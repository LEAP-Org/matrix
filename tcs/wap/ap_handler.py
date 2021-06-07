# -*- coding: utf-8 -*-
"""
LEAP™ Access Point Handler
==========================
Contributors: Christian Sargusingh
Modified: 2020-07
Repository: https://github.com/LEAP-Org/LEAP
README available in repository root
Version: 1.0

Dependencies
------------
 
Copyright © 2020 LEAP. All Rights Reserved.
"""
import logging

from tcs.event.registry import EventRegistry
from tcs.wap.socket import SocketHandler

class ApHandler:

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.socket = SocketHandler()
        # register shutdown ISR
        with EventRegistry() as event:
            event.register('APR_VALIDATED', self.init_connection)
            event.register('POST_FRAMECNT', self.post_frame_count)
        self.log.info("%s successfully instantiated", __name__)

    def init_connection(self):
        #self.log.info("Initializing receiver at AP: %s", ap_index)
        #self.socket.register(ap_index)
        # Notify success
        #self.socket.post_request(ap_index, obj=True, msg="Defining session at AP: {}".format(ap_index))
        with EventRegistry() as event:
            event.execute('FETCH_PAYLOAD')
    
    def post_frame_count(self, framecnt:int):
        self.socket.sendFrameNumber(framecnt)
    
    def run_server(self):
        bytestream = self.socket.run()
        #self.log.info("Received '%s' from socket", bytestream)
        with EventRegistry() as event:
            event.execute('TRANSMIT', bytestream)
            self.log.info("Executed transmission event")
