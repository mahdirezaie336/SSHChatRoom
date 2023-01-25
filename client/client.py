import sys
import socket
import getpass
import paramiko
from common import MESSAGE_LENGTH, WRONG_CREDENTIALS, LOGIN_SUCCESSFUL


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
        data = self.sock.recv(MESSAGE_LENGTH)
        return data

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    address, port = sys.argv[1], int(sys.argv[2])
    client = Client(address, port)
    client.connect()
    while True:
        username = input("Username: ")
        password = getpass.getpass("Password: ")

        client.send(username)
        client.send(password)

        server_feedback = client.receive().decode()
        
        if server_feedback == WRONG_CREDENTIALS:
            print("Wrong credentials, try again.")
        
        break

    # Get messages from user
    while True:
        message = input("Enter a message: ")
        client.send(message.encode())
        print(client.receive().decode())