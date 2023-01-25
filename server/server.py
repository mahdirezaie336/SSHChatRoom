import threading
import socket
import json
import paramiko
from paramiko.common import AUTH_FAILED, AUTH_SUCCESSFUL
from common import MESSAGE_LENGTH

paramiko.ServerInterface

# A server to handle multiple clients in separate threads
class Server(paramiko.ServerInterface):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}

    def check_auth_password(self, username: str, password: str) -> int:
        users: dict = json.load(open("users.json", "r"))
                
        try:
            user_password = users[username]
            if password != user_password:
                raise KeyError
        except KeyError:
            return paramiko.ServerInterface

        
        return super().check_auth_password(username, password)

    def handle_client(self, client_socket: socket.socket, address: socket._RetAddress) -> None:
        try:
            while True:
                username = client_socket.recv(MESSAGE_LENGTH).decode()
                password = client_socket.recv(MESSAGE_LENGTH).decode()
                users: dict = json.load(open("users.json", "r"))
                
                try:
                    user_password = users[username]
                    if password != user_password:
                        raise KeyError
                except KeyError:
                    client_socket.send(WRONG_CREDENTIALS.encode())
                    client_socket.close()
                    return

                client_socket.send(LOGIN_SUCCESSFUL.encode())
                
                transport = paramiko.Transport(client_socket)
                transport.add_server_key(paramiko.RSAKey(filename="id_rsa"))
                transport.start_server(self)

        except ConnectionResetError:
            print("Client disconnected")
            client_socket.close()
            self.connections.remove(threading.current_thread())

    def run(self):
        print("Starting server on address ", self.host, " and port ", self.port)
        self.socket.bind((self.host, self.port))

        # Listen for connections
        print("Listening for connections ...")
        self.socket.listen()
        try:
            while True:
                client_socket, address = self.socket.accept()
                print("Received connection from ", address)
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_handler.start()
                self.connections.append(client_handler)
        except KeyboardInterrupt:
            print("Shutting down server")
            self.socket.close()


if __name__ == "__main__":
    config = json.load(open("config.json", "r"))
    host, port = config["listen_address"], config["listen_port"]
    server = Server(host, port)
    server.run()
