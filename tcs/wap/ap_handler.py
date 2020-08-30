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

from tcs.event.handler import EventHandler

class ApHandler:

    def __init__(self, hostname):
        self.log = logging.getLogger(__name__)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # register shutdown ISR
        with EventHandler() as event:
            event.register('SHUTDOWN', self.shutdown)
        self.ap_thread = Thread(target=self.start,daemon=True)
        self.host = os.environ.get('HOSTNAME')
        self.port = int(os.environ.get('PORT'))
        # Uplink socket bind
        try:
            self.soc.bind((self.host, self.port))
        except ConnectionError as exc:
            # Protect against multiple instances by checking the server port
            self.log.exception("""TCU initialization failed. Server socket bind encountered a 
                connection error: %s""", exc)
            raise ConnectionError from exc
        else:
            self.log.info("Server socket bind successful")
        self.log.info("%s successfully instantiated", __name__)

    def start(self):
        self.ap_listener()

    # TODO: Method too complicated. Seperation of concerns
    def ap_listener(self):
        """This function listens for receiver connections at well-known server ports. The function
        receives the APR key sent by the receiver and checks it against TCU `Cache`. If there is a
        match then we register the receiver with a custom `SessionQueue` object. Otherwise we
        return an error message back over the socket indicating the key is invalid. If the 
        `SessionQueue` instantiation fails the function also notifies the receiver over the `socket`
        connection.
        """
        # while True:
        #     self.log.info("Waiting for receiver request on port %s", self.port)
        #     self.soc.listen()
        #     conn, addr = self.soc.accept()
        #     with conn:
        #         self.log.info("Connected by device at: %s", addr)
        #         # receive a bitarray object
        #         apr = pickle.loads(conn.recv(2048))
        #         self.log.info("Validating received APR key: %s", apr)
        #         # APR verification
        #         try:
        #             ap_index = self.cache.check(apr)
        #         except ValueError:
        #             self.log.warning("APR key %s revoked.", apr)
        #             # Notify failure 
        #             conn.send(pickle.dumps(False))
        #             conn.send(("Access Point Registry invalid. Request declined.").encode('utf-8'))                     
        #         else:
        #             self.log.info("Validated APR key: %s", apr)
        #             # Notify success
        #             conn.send(pickle.dumps(True))
        #             self.log.info("Defining session at AP: %s", ap_index)
        #             frame_cnt, files = self.get_attributes()
        #             self.log.info("Sending frame counts: %s", frame_cnt)
        #             conn.send(pickle.dumps(frame_cnt))
        #             self.log.info("Sending file names: %s", files)
        #             time.sleep(1)
        #             conn.send(pickle.dumps(files))
        #             file_index = pickle.loads(conn.recv(1024))
                    
        #             for _,index in enumerate(file_index):
        #                 files = self.file_list[index]
        #             self.log.info('Received Request for: %s', files)
 
        #             self.log.info("Initializing receiver at AP: %s", ap_index)
        #             try:
        #                 self.session_init(ap_index, file_index)
        #             except MemoryError:
        #                 conn.send(pickle.dumps(False))
        #                 conn.send(("Transmitter capacity reached.").encode('utf-8'))
        #             except IndexError:
        #                 conn.send(pickle.dumps(False))
        #                 conn.send(("Receiver already registered at AP " +
        #                            str(ap_index)).encode('utf-8'))
        #             except ValueError:
        #                 self.log.warning("Detected internal error in session instantiation.")
        #                 conn.send(pickle.dumps(False))
        #                 conn.send(("""Request terminated: Detected internal error in session 
        #                     instantiation.""").encode('utf-8'))
        #             else:
        #                 conn.send(pickle.dumps(True))

    def shutdown(self):
        """ ISR bound to SHUTDOWN """
        self.log.info("Closing network sockets...")
        self.soc.close()
        self.log.info("complete")