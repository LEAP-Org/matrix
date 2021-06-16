#!/usr/bin/env python3
import sys
import socket
import logging
import binascii
import requests
import json
import time

from typing import Tuple


logging.basicConfig(
    format="%(asctime)s %(levelname)s client %(message)s",
    level=logging.DEBUG
)


class Client:

    def __init__(self, host: str, port: int):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))
        self.message = None

    def run(self, message: str):
        self.message = message
        logging.info("Sending echo message: %s", message)
        self.soc.send(message.encode())
        logging.debug("sent first message")
        for i in range(len(self.message)):
            time.sleep(0.25)
            self.receive_frame(i)
        self.soc.close()

    def create_msg(self, crcval: int, msg: str) -> str:
        packet = str(crcval) + '~' + msg
        return packet

    def send(self, data: str) -> None:
        self.soc.send(data.encode())
        logging.debug("Sent message: %s", data)

    def receive(self) -> Tuple[int, str, int]:
        response = self.soc.recv(1024)
        logging.debug("recmsg: %s at addr: %s", response, self.soc.getsockname())
        cached_crc = binascii.crc32(response)
        str_crc, resp = response.decode().split('~')
        crc = int(str_crc)
        logging.debug("crc: %s, resp: %s", crc, resp)
        return crc, resp, cached_crc

    def receive_frame(self, index: int):
        crc, resp, cached_crc = self.receive()
        # issue event to capture
        if resp == "UP":
            crc_simulated_capture = binascii.crc32(self.message[index].encode())
            # note: replace samplecrc with captured crc
            logging.debug("captured crc: %s", crc_simulated_capture)
            # verify captured crc of data matches server sent crc
            if crc == crc_simulated_capture:
                self.send(self.create_msg(cached_crc, "ACK"))
            else:
                self.send(self.create_msg(cached_crc, "NACK"))


if __name__ == "__main__":
    args = sys.argv[1:]
    message = args[0]
    apr = args[1]
    response = requests.get('http://localhost:5000/v1/register',
                            headers={'Content-Type': 'application/json', 'Apr': apr})
    payload: dict = json.loads(response.content)
    port = payload.get('port')
    if port is None:
        raise RuntimeError
    c = Client(host='localhost', port=port)
    c.run(message)
