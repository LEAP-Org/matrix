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
import pickle
import socket
from threading import Thread
import logging.config

from tcs.event.registry import EventRegistry

class ApHandler:

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # register shutdown ISR
        with EventRegistry() as event:
            event.register('SHUTDOWN', self.shutdown)
            event.register('APR_VALIDATED', self.init_connection)
            event.register('POST_REQUEST', self.post_request)
        self.ap_thread = Thread(target=self.start,daemon=True)
        self.host = os.environ.get('HOSTNAME')
        self.port = int(os.environ.get('PORT'))
        self.conn, self.addr = None, None
        self.log.info("%s successfully instantiated", __name__)

    def start(self):
        # Uplink socket bind
        try:
            self.soc.bind((self.host, self.port))
        except ConnectionError as exc:
            # Protect against multiple instances by checking the server port
            self.log.exception("""TCU initialization failed. Server socket bind encountered a 
                connection error: %s""", exc)
        else:
            self.log.info("Server socket bind successful. Initializing listener thread")
            Thread(target=self.ap_listener, daemon=True).start()

    # TODO: Method too complicated. Seperation of concerns
    def ap_listener(self):
        """This function listens for receiver connections at well-known server ports. The function
        receives the APR key sent by the receiver and checks it against TCU `Cache`. If there is a
        match then we register the receiver with a custom `SessionQueue` object. Otherwise we
        return an error message back over the socket indicating the key is invalid. If the 
        `SessionQueue` instantiation fails the function also notifies the receiver over the `socket`
        connection.
        """
        while True:
            self.log.info("Waiting for receiver request on port %s", self.port)
            self.soc.listen()
            self.conn, self.addr = self.soc.accept()
            self.log.info("Connected by device at: %s", self.addr)
            # receive a bitarray object
            apr = self.get_request()
            self.log.info("Validating received APR key: %s", apr)
            # APR verification
            with EventRegistry() as event:
                event.execute('VALIDATE_APR', apr)

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
            
    def post_request(self, obj:object, msg:str=""):
        """
        This function is bound to event:POST_REQUEST. It pickles an object to the client and sends
        an optional message.

        :param obj: object to pickle to client
        :param msg: optional message to client
        """
        with self.conn as conn:
            conn.send(pickle.dumps(obj))
            if len(msg) > 0:
                conn.send((msg).encode('utf-8'))

    def get_request(self, size:int=2048):
        """
        This function is bound to event:POST_REQUEST. It pickles an object to the client and sends
        an optional message.

        :param size: size for byte load (default fo 2048)
        :return: object pickled from client
        """
        with self.conn as conn:
            return pickle.loads(conn.recv(size))

    def shutdown(self):
        """
        This function is bound to event:SHUTDOWN. It simply closes the active socket
        """
        self.log.info("Closing network sockets...")
        self.soc.close()
        self.log.info("socket shutdown complete")