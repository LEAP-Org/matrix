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
import time
import os
from threading import Thread
import logging.config

from tcs.event.registry import EventRegistry
from tcs.wap.socket import SocketHandler

class ApHandler:

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.socket = SocketHandler()
        # register shutdown ISR
        with EventRegistry() as event:
            event.register('APR_VALIDATED', self.init_connection)
        self.log.info("%s successfully instantiated", __name__)

    def init_connection(self, ap_index:int):
        """
        """
        self.log.info("Initializing receiver at AP: %s", ap_index)
        # Notify success
        self.post_request(True, msg="Defining session at AP: {}".format(ap_index))
        frame_cnt, files = self.get_attributes() # generate file list and counts on request
        self.log.info("Sending frame counts: %s and file names: %s", frame_cnt, files)
        self.post_request(obj=(frame_cnt,files))
        file_index = self.get_request()
        for _,index in enumerate(file_index):
            files = self.file_list[index]
        self.log.info('Received Request for: %s', files)
        with EventRegistry() as event:
            event.execute('SESSION_INIT', ap_index)