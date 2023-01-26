import sys
import socket
import getpass
import paramiko
from common import MESSAGE_LENGTH, AUTH_FAILED, AUTH_SUCCESSFUL, GET_ONLINES, ACK


class Client():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self, addr, port) -> None:
        self.sock.connect((addr, port))

    def tunnel(self) -> None:
        self.user_authenticate()
        self.transport = paramiko.Transport(self.sock)
        self.transport.start_client()
        self.ssh_authenticate()
        self.channel = self.transport.open_session()

    def user_authenticate(self) -> None:
        self.username = input("Username: ")
        password = getpass.getpass("Password: ")
        self.sock.sendall(self.username.encode())
        self.sock.sendall(password.encode())
        server_feedback = self.sock.recv(MESSAGE_LENGTH)
        if server_feedback == AUTH_SUCCESSFUL:
            print("Login successful")
        elif server_feedback == AUTH_FAILED:
            print("Wrong credentials, try again later")
            sys.exit()

    def ssh_authenticate(self) -> None:
        try:
            self.transport.auth_none(self.username)
            print("Created ssh tunnel")
        except paramiko.AuthenticationException:
            print("Could not create ssh tunnel, try again later")
            sys.exit()

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
        try:
            message = input("Enter a message: ")
            client.send(message.encode())
            if message == GET_ONLINES:
                print("Online users:")
                onlines_count = int(client.receive().decode())
                client.send(ACK)
                for i in range(onlines_count):
                    print(i, ":", client.receive().decode())    
                    client.send(ACK)
            else:
                print(client.receive().decode())
        except KeyboardInterrupt:
            break