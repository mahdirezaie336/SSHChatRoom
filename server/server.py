import threading
import socket
import json
import paramiko
from paramiko.common import AUTH_FAILED, AUTH_SUCCESSFUL, OPEN_SUCCEEDED
from common import MESSAGE_LENGTH

paramiko.ServerInterface

# A server to handle multiple clients in separate threads
class Server(paramiko.ServerInterface):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.online_users = {}

    def check_auth_password(self, username: str, password: str) -> int:
        users: dict = json.load(open("user.json", "r"))
        
        try:
            user_password = users[username]
            if password != user_password:
                raise KeyError
        except KeyError:
            return AUTH_FAILED

        return AUTH_SUCCESSFUL

    def check_channel_request(self, kind: str, chanid: int) -> int:
        return OPEN_SUCCEEDED

    def handle_client(self, client: socket.socket, address: socket._RetAddress) -> None:
        try:
            while True:
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
        self.sock.bind((self.host, self.port))

        # Listen for connections
        print("Listening for connections ...")
        transport = paramiko.Transport(self.sock)
        transport.add_server_key(paramiko.RSAKey(filename="id_rsa"))
        transport.start_server(server=self)

        try:
            while True:
                channel = transport.accept()
                print("Received connection from ", channel.chanid)
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=(channel)
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
