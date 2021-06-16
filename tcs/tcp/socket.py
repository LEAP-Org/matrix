"""
Socket Interface
================
Modified: 2021-06

Dependencies
------------

Copyright © 2021 LEAP. All Rights Reserved.
"""

import logging
import socket
import retry
import binascii
from typing import Optional, Tuple, Union

from tcs.tcp.config import APConfig as ac
from tcs.event.registry import Registry as events


class SocketInterface:

    def __init__(self, addr: str):
        self._log = logging.getLogger(__name__)
        host, port = addr.split(':')  # Port to listen on (non-privileged ports are > 1023)
        self.address = (host, int(port))
        # socket for client connection
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind(self.address)
        self.client_connection: Optional[socket.socket] = None
        self._log.info("%s successfully instantiated", __name__)

    def __del__(self):
        self.soc.close()
        self._log.info("Closed socket and dereferenced %s", self)

    def run(self):
        self.soc.listen()
        self.client_connection, addr = self.soc.accept()
        self._log.debug("connection from %s", addr)
        # receive ready response from client
        data = self.client_connection.recv(1024)
        self._log.debug("echo message from client: %s", data)
        frames = len(data)
        self._log.debug("number of transmission frames: %s", frames)
        events.enqueue.execute(data)
        try:
            for b in data:
                events.uplink.execute()
                self.send_frame(b.to_bytes(1, byteorder='little'))
        except (RuntimeError, socket.error) as exc:
            logging.exception("Maximum retry limit reached: \n%s", exc)
        self.client_connection.close()
        del self

    def send(self, data: Union[str, int]):
        if type(data) is str: self.client_connection.send(data.encode())
        elif type(data) is int: self.client_connection.send(bytes([data]))
        logging.info("sent: %s to address: %s", data, self.client_connection.getsockname())

    def receive(self) -> Tuple[int, str]:
        response = self.client_connection.recv(1024)
        logging.debug("msgback: %s", response)
        # parse msg back
        str_crc, resp = response.decode().split('~')
        crc = int(str_crc)
        logging.debug("crc: %s, resp: %s", crc, resp)
        return crc, resp

    def createmsg(self, crcval, msg) -> str:
        newmsg = str(crcval) + '~' + msg
        return newmsg

    @retry.retry(socket.error, tries=1)
    @retry.retry(RuntimeError, tries=5)
    def send_frame(self, data: bytes) -> None:
        # store current crc32 data
        frame_crc = binascii.crc32(data)
        # store expected response
        packet_crc = binascii.crc32(self.createmsg(frame_crc, 'UP').encode())
        self.send(self.createmsg(frame_crc, 'UP'))
        # receive response from client
        crc, resp = self.receive()
        # cube capture failed
        if crc == packet_crc and resp == 'NACK':
            logging.exception("Detected client tesseract capture error")
            raise RuntimeError
        # socket data scrambled
        if crc != packet_crc and resp == 'NACK':
            logging.exception("Detected socket error")
            raise socket.error
