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
        print(username, password)
        users: dict = json.load(open("users.json", "r"))
        try:
            user_password = users[username]
            if password != user_password:
                raise KeyError
        except KeyError:
            return AUTH_FAILED

        return AUTH_SUCCESSFUL

    def check_channel_request(self, kind: str, chanid: int) -> int:
        return OPEN_SUCCEEDED

    def handle_client(self, client_channel: paramiko.Channel) -> None:
        try:
            while True:
                data = client_channel.recv(MESSAGE_LENGTH)
                print(data.decode())
                client_channel.sendall("ACK".encode())
                
        except ConnectionResetError:
            print("Client disconnected")
            client_channel.close()
            self.connections.remove(threading.current_thread())

    def run(self):
        print("Starting server on address ", self.host, " and port ", self.port)
        self.sock.bind((self.host, self.port))

        # Listen for connections
        print("Listening for connections ...")
        self.sock.listen()

        try:
            while True:
                client_socket, addr = self.sock.accept()
                transport = paramiko.Transport(client_socket)
                transport.add_server_key(paramiko.RSAKey(filename="id_rsa"))
                transport.start_server(server=self)
                channel = transport.accept()
                print("Received connection from ", channel.chanid)
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=[channel]
                )
                client_handler.start()
                self.connections.append(client_handler)
        except KeyboardInterrupt:
            print("Shutting down server")
            self.socket.close()


if __name__ == "__main__":
    config = json.load(open(file="config.json", mode="r", encoding="UTF-8"))
    host, port = config["listen_address"], config["listen_port"]
    server = Server(host, port)
    server.run()
