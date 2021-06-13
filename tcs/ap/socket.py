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

from tcs.ap.config import APConfig as ac


class SocketInterface:

    mainClientSocket = None

    def __init__(self, addr: str):
        self._log = logging.getLogger(__name__)
        self.host, port = addr.split(':')  # Port to listen on (non-privileged ports are > 1023)
        self.port = int(port)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.host, self.port))
        self._log.info("bound socket to %s:%s", self.host, self.port)
        self.shutdown = False
        self._log.info("%s successfully instantiated", __name__)

    def run(self):
        while not self.shutdown:
            self.soc.listen()
            clientsocket, addr = self.soc.accept()
            self.mainClientSocket = clientsocket
            with clientsocket:
                self._log.debug("connection from %s", addr)
                # clientsocket.send(bytes("r", "utf-8"))
                data = clientsocket.recv(1024)
                self._log.debug("data: %s", data)
                if data.decode() == "r":
                    self.sendData(ac.SENSITIVE_DATA)
        # after main event loop exits close the socket
        self.soc.close()

    def sendmsg(self, msg):
        emsg = msg.encode()
        self.mainClientSocket.send(emsg)

    def parityCheck(self, bitdata):
        counter = 0
        for b in bitdata:
            if b == "1":
                counter = counter + 1
        return counter % 2

    def sendFrameNumber(self, numFrames):
        self.mainClientSocket.send(numFrames)

    def sendData(self, arrofb):
        for i in range(ac.FRAME_CNT):
            # creating random data to send
            bdata = "{0:08b}".format(arrofb[i] & 0xff)
            self._log.debug("bdata: %s", bdata)
            if self.parityCheck(bdata) % 2 == 0:
                self.sendmsg("0")
                self._log.debug("sent 0 as parity")
            else:
                self.sendmsg("1")
                self._log.debug("sent 1 as parity")
            # send data
            msgback = self.mainClientSocket.recv(1024)
            self._log.debug("msgback: %s", msgback)
            if msgback.decode() == "l":
                self._log.debug("request to send last capture")
                # send last capture
            elif msgback.decode() != "rec":
                self._log.debug("breaked")
                break

    def close(self) -> None:
        """
        Kill main event loop
        """
        self.shutdown = True
