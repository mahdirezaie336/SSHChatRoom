import sys
import socket
import json
import hashlib


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.host, self.port))

    def send(self, data):
        self.sock.sendall(data)

    def receive(self):
        data = self.sock.recv(1024)
        return data

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    # Get host and port from command line arguments
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = "localhost"
        port = 8080

    client = Client(host, port)
    client.connect()

    # Send username and password as json
    password = hashlib.sha256("pwd".encode()).hexdigest()
    data = {"username": "mahdirezaie336", "password": password}
    client.send(json.dumps(data).encode("utf-8"))
    print(client.receive().decode("utf-8"))

    # Get messages from user
    while True:
        message = input("Enter a message: ")
        client.send(message.encode())
        print(client.receive().decode())
