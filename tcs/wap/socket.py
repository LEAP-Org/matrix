"""
LEAP™ Socket Handler
====================
Contributors: Christian Sargusingh
Modified: 2020-08
Repository: https://github.com/LEAP-Org/LEAP
README available in repository root
Version: 

Dependencies
------------

Copyright © 2020 LEAP. All Rights Reserved.
"""

import os
import logging.config
import pickle
import socket
from threading import Thread

from tcs.event.registry import EventRegistry

class SocketHandler:
    
    _socket_registry = [None for _ in range(4)]

    def __init__(self):
        self.log = logging.getLogger(__name__)
        
        with EventRegistry() as event:
            event.register('SHUTDOWN', self.shutdown)
            event.register('POST_REQUEST', self.post_request)
            event.register('GET_REQUEST', self.get_request)
        # Thread(target=self.request_listener, daemon=True).start()
        self.log.info("%s successfully instantiated", __name__)

    def request_listener(self):
        """
        """
        hostname = os.environ.get('HOSTNAME')
        port = int(os.environ.get('PORT'))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            # Uplink socket bind
            try:
                soc.bind((hostname, port))
            except ConnectionError as exc:
                # Protect against multiple instances by checking the server port
                self.log.exception("TCU initialization failed. Server socket bind encountered a connection error: %s",exc)
                raise ConnectionError from exc
            else:
                self.log.info("Server socket bind successful. Initializing listener thread")
                self.log.info("Waiting for receiver request on port %s", port)
                soc.listen()
                conn, addr = soc.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data)
                self.log.info("Connected by device at: %s", addr)
                # make unauthenticated request to get apr key
                # apr = self.get_request()
                # self.log.info("Validating received APR key: %s", apr)
                # # APR verification
                # with EventRegistry() as event:
                #     event.execute('VALIDATE_APR', apr)
    
    def register(self, ap_index:int):
        """
        """
        # self._socket_registry[ap_index] = (self.conn, self.addr)

    def post_request(self, ap_index, obj:object, msg:str=""):
        """
        This function is bound to event:POST_REQUEST. It pickles an object to the client and sends
        an optional message.

        :param obj: object to pickle to client
        :param msg: optional message to client
        """
        # with self._socket_registry[ap_index][0] as conn:
        #     conn.send(pickle.dumps(obj))
        #     if len(msg) > 0:
        #         conn.send((msg).encode('utf-8'))

    def get_request(self, ap_index:int=-1, size:int=2048):
        """
        This function is bound to event:POST_REQUEST. It pickles an object to the client and sends
        an optional message.

        :param ap_index: the access point socket for the get request. If None the request is unauthenticated
        :param size: size for byte load (default fo 2048)
        :return: object pickled from client
        """
        # if ap_index == -1:
        #     connection = self.conn
        # else:
        #     connection = self._socket_registry[ap_index][0]
        # with connection as conn:
        #     return pickle.loads(conn.recv(size))

    def shutdown(self):
        """
        This function is bound to event:SHUTDOWN. It simply closes the active socket
        """
        # self.log.info("Closing network sockets...")
        # self.soc.close()
        # self.log.info("socket shutdown complete")