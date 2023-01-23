import sys
import socket


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
    address, port = sys.argv[1], int(sys.argv[2])
    client = Client(address, port)
    client.connect()

    # Get messages from user
    while True:
        message = input("Enter a message: ")
        client.send(message.encode())
        print(client.receive().decode())