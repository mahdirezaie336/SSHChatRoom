import threading
import socket
import json
import paramiko
from paramiko.common import AUTH_FAILED, AUTH_SUCCESSFUL, OPEN_SUCCEEDED
import common

paramiko.ServerInterface

# A server to handle multiple clients in separate threads
class Server(paramiko.ServerInterface):
    def __init__(self, host, port):
        self.users: dict = json.load(open("users.json", "r"))
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.online_users = {}

    def check_auth_none(self, username: str) -> int:
        try:
            if not username in self.users.keys():
                raise KeyError
        except KeyError:
            return AUTH_FAILED
        
        return AUTH_SUCCESSFUL

    def retrieve_online_users(self, channel: paramiko.Channel) -> None:
        channel.sendall(str(len(self.online_users)).encode())
        channel.recv(common.MESSAGE_LENGTH)
        for online_user in self.online_users.keys():
            channel.sendall(online_user.encode())
            channel.recv(common.MESSAGE_LENGTH)

    def deliver_msg(self, username: str, channel: paramiko.Channel, data: bytes) -> None:
        try:
            target_username = data[1]
            target_channel: paramiko.Channel = self.online_users[target_username]
            message = str.join(" ", data[2:])
            message = username + ": " + message
            print(message)
            target_channel.sendall(message.encode())
            channel.sendall("Sent".encode())
        except IndexError:
            channel.sendall("Incorrect message format".encode())
        except KeyError:
            channel.sendall("Client is offline".encode())

    def serve_client(self, username: str, channel: paramiko.Channel) -> None:
        data = channel.recv(common.MESSAGE_LENGTH)
        if data.decode() == "[onlineusers]":
            self.retrieve_online_users(channel)
        else:
            data = data.decode().split(sep=" ")
            try:
                if data[0] == "[msg]":
                    self.deliver_msg(username, channel, data)
                else:
                    raise IndexError
            except IndexError:
                channel.sendall("Unknown command".encode())

    def check_channel_request(self, kind: str, chanid: int) -> int:
        return OPEN_SUCCEEDED

    def handle_client(self, client_socket: socket.socket) -> None:
        username = client_socket.recv(common.MESSAGE_LENGTH).decode()
        password = client_socket.recv(common.MESSAGE_LENGTH).decode()

        try:
            if password != self.users[username]:
                raise KeyError
        except KeyError:
            client_socket.sendall(common.AUTH_FAILED.encode())
            client_socket.close()
            self.online_users.pop(username)
            self.connections.remove(threading.current_thread())
            return

        client_socket.sendall(common.AUTH_SUCCESSFUL.encode())
        self.online_users[username] = "Pending..."
        
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(paramiko.RSAKey(filename="id_rsa"))
        transport.start_server(server=self)
        channel = transport.accept()
        print("Received connection from ", channel.chanid)
        self.online_users[username] = channel
        
        try:
            while True:
                self.serve_client(username, channel)
                
        except socket.error:
            print("Client disconnected")
            transport.close()
            client_socket.close()
            self.online_users.pop(username)
            self.connections.remove(threading.current_thread())

    def run(self):
        print("Starting server on address ", self.host, " and port ", self.port)
        self.sock.bind((self.host, self.port))

        try:
            # Listen for connections
            print("Listening for connections ...")
            self.sock.listen()
            while True:
                client_socket, addr = self.sock.accept()
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=[client_socket]
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
