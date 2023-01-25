import threading
import socket
import json
import paramiko
from mydatabase.jsondatabase import JsonDatabase


# A server to handle multiple clients in separate threads
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.db = JsonDatabase('./mydatabase/users.json')
        self.connections = []

    def authenticate(self, username, password):
        return self.db.authenticate(username, password)

    def handle_client(self, client_socket, address):
        # Get username and password from socket as json
        data = client_socket.recv(1024)
        data = json.loads(data.decode("utf-8"))
        username = data["username"]
        password = data["password"]

        # Authenticate user
        if not self.authenticate(username, password):
            print("Authentication failed for user ", username)
            client_socket.close()
            return

        # Create ssh server
        ssh_server = paramiko.ServerInterface()
        ssh_server.get_allowed_auths = lambda username: "password"
        ssh_server.check_auth_password = lambda username, password: paramiko.AUTH_SUCCESSFUL
        ssh_server.get_banner = lambda: "Welcome to my server"
        ssh_server.check_channel_request = lambda kind, chanid: paramiko.OPEN_SUCCEEDED
        ssh_server.check_channel_shell_request = lambda channel: True
        ssh_server.check_channel_pty_request = lambda channel, term, width, height, pixelwidth, pixelheight, modes: True

        # Create transport
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(paramiko.RSAKey(filename="./server/ssh_keys/id_rsa"))
        transport.start_server(server=ssh_server)

        # Wait for client to connect
        channel = transport.accept()
        print("Client connected")

        # Send welcome message
        channel.send(b"Welcome to my server\r\n")

        # # Start the server
        # try:
        #     while True:
        #         data = client_socket.recv()
        #         print("Received data from ", address, ": ", data.decode())
        #         client_socket.send("ACK".encode())
        # except ConnectionResetError:
        #     print("Client disconnected")
        #     client_socket.close()
        #     self.connections.remove(threading.current_thread())

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
