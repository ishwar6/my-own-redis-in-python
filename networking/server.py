import socket
import threading
import time
import argparse

class InMemoryStore:
    """
    Class to handle the storage of key-value pairs and their expiration times.
    """
    def __init__(self):
        self.store = {}
        self.expiration_store = {}

    def set(self, key, value, expiration_time=None):
        """
        Store a key-value pair with an optional expiration time.
        """
        self.store[key] = value
        if expiration_time:
            self.expiration_store[key] = time.time() * 1000 + expiration_time   

    def get(self, key):
        """
        Retrieve a key-value pair, checking if it has expired.
        """
        if key in self.expiration_store:
            if time.time() * 1000 >= self.expiration_store[key]:
                self.delete(key)
                return None
        return self.store.get(key)

    def delete(self, key):
        """
        Delete a key from the store.
        """
        if key in self.store:
            del self.store[key]
        if key in self.expiration_store:
            del self.expiration_store[key]

class RESPParser:
    """
    Class to handle the parsing of RESP-formatted commands.
    """
    @staticmethod
    def parse(data: str):
        """
        Parse a RESP-formatted command into an array of elements.
        """
        lines = data.split("\r\n")
        if len(lines) < 3 or not lines[0].startswith("*"):
            return None

        num_elements = int(lines[0][1:])
        elements = []
        i = 1
        while i < len(lines):
            if lines[i].startswith("$"):
                length = int(lines[i][1:])
                elements.append(lines[i + 1])
                i += 2
            else:
                i += 1
        return elements if len(elements) == num_elements else None

class RedisServer:
    """
    Class to represent the Redis-like server, handling client connections and commands.
    """
    def __init__(self, host="localhost", port=6380, rdb_dir="/tmp/redis-data", rdb_filename="rdbfile"):
        self.store = InMemoryStore()
        self.host = host
        self.port = port
        self.rdb_dir = rdb_dir
        self.rdb_filename = rdb_filename

    def start(self):
        """
        Start the Redis server and listen for incoming connections.
        """
        with socket.create_server((self.host, self.port), reuse_port=True) as server_socket:
            server_socket.listen()
            print(f"Server started on {self.host}:{self.port}. Logs will appear here.")
            while True:
                conn, addr = server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        """
        Handle a client connection, process commands, and send responses.
        """
        with conn:
            try:
                while True:
                    request = conn.recv(512)
                    if not request:
                        break
                    print(request)
                    command = RESPParser.parse(request.decode())
                    if command:
                        self.process_command(conn, command)
            except ConnectionResetError:
                pass

    def process_command(self, conn, command):
        """
        Process a parsed RESP command and send the appropriate response.
        """
        cmd_name = command[0].lower()
        if cmd_name == "ping":
            conn.send(b"+PONG\r\n")
        elif cmd_name == "echo" and len(command) > 1:
            message = command[1]
            conn.send(f"${len(message)}\r\n{message}\r\n".encode())
        elif cmd_name == "set":
            self.handle_set_command(conn, command)
        elif cmd_name == "get":
            self.handle_get_command(conn, command)
        elif cmd_name == "config":
            self.handle_config_command(conn, command)

    def handle_set_command(self, conn, command):
        """
        Handle the SET command with optional PX expiration time.
        """
        key, value = command[1], command[2]
        expiration_time = None
        if len(command) >= 5 and command[3].lower() == "px":
            try:
                expiration_time = int(command[4])
            except ValueError:
                conn.send(b"-ERR invalid expiration time\r\n")
                return
        self.store.set(key, value, expiration_time)
        conn.send(b"+OK\r\n")

    def handle_get_command(self, conn, command):
        """
        Handle the GET command and check for key expiration.
        """
        key = command[1]
        value = self.store.get(key)
        if value is None:
            conn.send(b"$-1\r\n")
        else:
            conn.send(f"${len(value)}\r\n{value}\r\n".encode())

    def handle_config_command(self, conn, command):
        """
        Handle the CONFIG GET command for retrieving configuration parameters.
        """
        if len(command) >= 3 and command[1].lower() == "get":
            param = command[2].lower()
            if param == "dir":
                response = f"*2\r\n$3\r\ndir\r\n${len(self.rdb_dir)}\r\n{self.rdb_dir}\r\n"
            elif param == "dbfilename":
                response = f"*2\r\n$10\r\ndbfilename\r\n${len(self.rdb_filename)}\r\n{self.rdb_filename}\r\n"
            else:
                # Respond with null if the parameter is unknown
                response = "$-1\r\n"  
            conn.send(response.encode())

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Start a Redis-like server with RDB persistence.")
    parser.add_argument("--dir", default="/tmp/redis-data", help="Directory for RDB file")
    parser.add_argument("--dbfilename", default="rdbfile", help="RDB filename")
    args = parser.parse_args()

    # Initialize the server with command-line arguments
    server = RedisServer(rdb_dir=args.dir, rdb_filename=args.dbfilename)
    server.start()

if __name__ == "__main__":
    main()
