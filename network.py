
import socket

import config


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = config.host
        self.port = config.port
        self.addr = (self.host, self.port)
        response = self.connect()
        self.id, self.i = response.split('|')
        self.i = int(self.i)

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(2048).decode()

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error:
            raise
