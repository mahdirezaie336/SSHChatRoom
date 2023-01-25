import sys
import socket
import getpass
import paramiko
from common import MESSAGE_LENGTH


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self, addr, port) -> None:
        self.sock.connect((addr, port))

    def tunnel(self) -> None:
        self.transport = paramiko.Transport(self.sock)
        self.transport.start_client()
        self.authenticate()
        self.channel = self.transport.open_session()

    def authenticate(self) -> None:
        while True:
            username = input("Username: ")
            password = getpass.getpass("Password: ")

            try:
                self.transport.auth_password(username, password)
                print("Login successful")
                break
            except paramiko.AuthenticationException:
                print("Wrong Credentials, try again")

    def send(self, data):
        self.channel.sendall(data)

    def receive(self):
        data = self.channel.recv(MESSAGE_LENGTH)
        return data

    def close(self):
        self.transport.close()
        self.sock.close()


if __name__ == "__main__":
    
    address, port = sys.argv[1], int(sys.argv[2])
    client = Client()
    client.connect(address, port)
    client.tunnel()
    
    # Get messages from user
    while True:
        message = input("Enter a message: ")
        client.send(message.encode())
        print(client.receive().decode())