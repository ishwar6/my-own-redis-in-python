import socket
import logging

class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 3100):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self) -> None:
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            print(f"Server started at http://{self.host}:{self.port}")
            self.accept_connections()
        finally:
            self.server_socket.close()

    def accept_connections(self) -> None:
        while True:
            conn, addr = self.server_socket.accept()
            with conn:
                logging.info(f"Connected by {addr}")
                request_handler = RequestHandler(conn)
                request_handler.process_request()


class RequestHandler:
    def __init__(self, conn):
        self.conn = conn

    def process_request(self):
        # This method would handle incoming requests
        request = self.conn.recv(1024).decode('utf-8')
        logging.info(f"Received request: {request}")
        self.conn.sendall(b"HTTP/1.1 200 OK\n\nHello, World!")



if __name__ == "__main__":
    a = Server()
    a.start()
    a.accept_connections()

# Blocking I/O:

# The server uses the accept() method in a loop to accept incoming connections. This call blocks until a new connection is made.
# After accepting a connection, it handles the request using the RequestHandler class.
# The recv() method is used for reading the incoming data, which also blocks until the data is received.


# import socket

# HOST = "127.0.0.1"
# PORT = 3100

# with socket.create_connection((HOST, PORT)) as sock:
#     sock.sendall(b"Hello, Server")
#     response = sock.recv(1024)
#     print(f"Received: {response.decode('utf-8')}")


## Updated code if we use Threading. 

import socket
import logging
import threading

class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 3100):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self) -> None:
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server started at http://{self.host}:{self.port}")
            self.accept_connections()
        finally:
            self.server_socket.close()

    def accept_connections(self) -> None:
        while True:
            conn, addr = self.server_socket.accept()
            logging.info(f"Connected by {addr}")
            # Start a new thread to handle the connection
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def handle_client(self, conn, addr):
        with conn:
            request_handler = RequestHandler(conn)
            request_handler.process_request()
            logging.info(f"Connection with {addr} closed")


class RequestHandler:
    def __init__(self, conn):
        self.conn = conn

    def process_request(self):
        # This method would handle incoming requests
        request = self.conn.recv(1024).decode('utf-8')
        logging.info(f"Received request: {request}")
        self.conn.sendall(b"HTTP/1.1 200 OK\n\nHello, World!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = Server()
    server.start()


