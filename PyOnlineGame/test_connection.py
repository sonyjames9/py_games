import socket
import json
import time as t

class Network:
    def __init__(self, name):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.name = name
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.client.sendall(self.name.encode())
            return json.loads(self.client.recv(2048))
        except Exception as err:
            self.disconnect(err)

    # def send_str(self, data):
    #     try:
    #         self.client.connect(self.addr)
    #         self.client.sendall(self.name.encode())
    #         return json.loads(self.client.recv(2048))
    #     except Exception as e:
    #         self.disconnect(e)

    def send(self, data):
        try:
            self.client.send(json.dumps(data).encode())
            return json.loads(self.client.recv(2048).decode())
        except socket.error as err:
            self.disconnect(err)

    def disconnect(self, msg):
        print("[EXCEPTION] Disconnected from server : ", msg)
        self.client.shutdown(0)
        # self.client.shutdown(socket.SHUT_WR)
        self.client.close()


network = Network("Py online game- Sony")
# print(network.connect())
print(network.send({1: []}))
# print(network.send("{0: []}"))
