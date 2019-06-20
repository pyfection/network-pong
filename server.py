from uuid import uuid4
import socket
from _thread import start_new_thread

import config


class Server:
    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ""
        self.port = config.port
        self.server_ip = socket.gethostbyname(self.host)
        self.clients = []
        self.positions = {}
        self.updates = {}

        try:
            self.connection.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))

        self.connection.listen(2)
        print("Waiting for a connection")

        while True:
            try:
                conn, addr = self.connection.accept()
            except KeyboardInterrupt:
                self.connection.close()
                raise
            uuid = str(uuid4())
            print("Connected to: ", addr, uuid)

            self.updates[uuid] = []
            for i, client in enumerate(self.clients):
                self.updates[client].append(f'{uuid}:{len(self.clients)}')
                self.updates[uuid].append(f'{client}:{i}')
            i = len(self.clients)
            self.clients.append(uuid)
            start_new_thread(self.threaded_client, (conn, i, uuid))

    def threaded_client(self, conn, i, uuid):
        conn.send(str.encode('|'.join((uuid, str(i)))))
        while True:
            try:
                data = conn.recv(2048)
                reply = data.decode('utf-8')
                if not data:
                    conn.send(str.encode("Goodbye"))
                    break
                else:
                    id, pos = reply.split(":")
                    self.positions[id] = pos

                    reply = '|'.join(('{id}:{pos}'.format(id=id, pos=pos) for id, pos in self.positions.items()))
                    for update in self.updates[uuid]:
                        reply += f'&{update}'
                    self.updates[uuid].clear()

                conn.sendall(str.encode(reply))
            except Exception as e:
                print(e)
                break

        print("Connection Closed")
        conn.close()
