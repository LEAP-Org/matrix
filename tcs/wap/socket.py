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
import logging
import socket
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s server %(message)s",
    level=logging.DEBUG
)

rList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
arrofb = bytearray(rList)


class SocketHandler:

    HOST = ''
    PORT = 0
    numofFrames = 0
    mainClientSocket = None

    def __init__(self, host='127.0.0.1', port=65432, numFrames=10):
        self.HOST = host  # Standard loopback interface address (localhost)
        self.PORT = port       # Port to listen on (non-privileged ports are > 1023)
        self.numofFrames = numFrames

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.HOST, self.PORT))
                while True:
                    s.listen()
                    clientsocket, addr = s.accept()
                    self.mainClientSocket = clientsocket
                    with clientsocket:
                        logging.debug("connection from %s", addr)
                        #clientsocket.send(bytes("r", "utf-8"))
                        data = clientsocket.recv(1024)
                        logging.debug("data: %s", data)
                        if data.decode() == "r":
                            self.sendData(arrofb)
        except:
            print("ERROR: NO CONNECTION")

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
        for i in range(self.numofFrames):
            # creating random data to send
            bdata = "{0:08b}".format(arrofb[i] & 0xff)
            logging.debug("bdata: %s", bdata)
            if self.parityCheck(bdata) % 2 == 0:
                self.sendmsg("0")
                logging.debug("sent 0 as parity")
            else:
                self.sendmsg("1")
                logging.debug("sent 1 as parity")
            # send data
            msgback = self.mainClientSocket.recv(1024)
            logging.debug("msgback: %s", msgback)
            if msgback.decode() == "l":
                logging.debug("request to send last capture")
                # send last capture
            elif msgback.decode() != "rec":
                logging.debug("breaked")
                break
