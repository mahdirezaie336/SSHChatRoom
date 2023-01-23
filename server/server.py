import threading
import socket
import json
import paramiko


# A server to handle multiple clients in separate threads
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []

    def handle_client(self, client_socket, address):
        try:
            while True:
                data = client_socket.recv(1024)
                print("Received data from ", address, ":", data.decode())
                client_socket.send("ACK".encode())
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
