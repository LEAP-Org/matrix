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
            event.register('NOTIFY_CLIENT', self.notify_status)
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
            with self.conn as conn:
                self.log.info("Connected by device at: %s", addr)
                # receive a bitarray object
                apr = pickle.loads(self.conn.recv(2048))
                self.log.info("Validating received APR key: %s", apr)
                # APR verification
                with EventRegistry() as event:
                    event.execute('VALIDATE_APR', apr)
        
    def init_connection(self, ap:int):
        """
        """
        self.log.info("Initializing receiver at AP: %s", ap_index)
        # Notify success
        with self.conn as conn:
            self.notify_status(True, "Defining session at AP: {}".format(ap_index))
            frame_cnt, files = self.get_attributes() # generate file list and counts on request
            self.log.info("Sending frame counts: %s", frame_cnt)
            conn.send(pickle.dumps(frame_cnt))
            self.log.info("Sending file names: %s", files)
            time.sleep(1)
            conn.send(pickle.dumps(files))
            file_index = pickle.loads(conn.recv(1024))

        for _,index in enumerate(file_index):
            files = self.file_list[index]
        self.log.info('Received Request for: %s', files)

        with EventRegistry() as event:
            event.execute('SESSION_INIT', ap)

    def notify_status(self, status:bool, msg:str):
        """
        This function is bound to event:NOTIFY_CLIENT. It dumps a boolean status of the requested 
        job and a message back to the connecting client.

        :param status: boolean flag for status result
        :param msg: message to client
        """
        with self.conn as conn:
            conn.send(pickle.dumps(status))
            conn.send((msg).encode('utf-8'))

    def notify_failure(self):
        with self.conn as conn:
            conn.send(pickle.dumps(False))
            conn.send(("Access Point Registry invalid. Request declined.").encode('utf-8'))

    def shutdown(self):
        """
        This function is bound to event:SHUTDOWN. It simply closes the active socket
        """
        self.log.info("Closing network sockets...")
        self.soc.close()
        self.log.info("socket shutdown complete")