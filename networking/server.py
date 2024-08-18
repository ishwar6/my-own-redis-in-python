import socket
import threading
import time
import argparse

class InMemoryStore:
    """
    Class to handle the storage of key-value pairs, their types, and expiration times.
    """
    def __init__(self):
        self.store = {}
        self.type_store = {}  # Store the type of each key
        self.expiration_store = {}

    def set(self, key, value, expiration_time=None):
        """
        Store a key-value pair with an optional expiration time.
        """
        self.store[key] = value
        self.type_store[key] = "string"  # Assume all values are strings for now
        if expiration_time:
            self.expiration_store[key] = time.time() * 1000 + expiration_time  # Store expiration time in milliseconds

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
        if key in self.type_store:
            del self.type_store[key]
        if key in self.expiration_store:
            del self.expiration_store[key]

    def get_type(self, key):
        """
        Retrieve the type of the value stored at the given key.
        """
        return self.type_store.get(key, "none")

    def add_stream_entry(self, key, entry_id, fields):
        """
        Add an entry to the stream stored at the key. If the stream doesn't exist, create it.
        """
        if key not in self.store:
            self.store[key] = []  
            self.type_store[key] = "stream"
        
        stream = self.store[key]
        entry = {"id": entry_id, **fields}
        stream.append(entry)
        return entry_id

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
    def __init__(self, host="localhost", port=6379, role="master"):
        self.store = InMemoryStore()
        self.host = host
        self.port = port
        self.role = role  # Role can be either 'master' or 'slave'
        
        # Initialize replication-related values
        self.master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"  # Hardcoded replication ID
        self.master_repl_offset = 0  # Start at offset 0

    def start(self):
        """
        Start the Redis server and listen for incoming connections.
        """
        with socket.create_server((self.host, self.port), reuse_port=True) as server_socket:
            server_socket.listen()
            print(f"Server started on {self.host}:{self.port}. Role: {self.role}")
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
        elif cmd_name == "type":
            self.handle_type_command(conn, command)
        elif cmd_name == "xadd":
            self.handle_xadd_command(conn, command)
        elif cmd_name == "info":
            self.handle_info_command(conn, command)

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

    def handle_type_command(self, conn, command):
        """
        Handle the TYPE command, returning the type of the value stored at the key.
        """
        key = command[1]
        value_type = self.store.get_type(key)
        conn.send(f"+{value_type}\r\n".encode())

    def handle_xadd_command(self, conn, command):
        """
        Handle the XADD command to append an entry to a stream.
        """
        key = command[1]
        entry_id = command[2]
        fields = dict(zip(command[3::2], command[4::2]))  

        added_entry_id = self.store.add_stream_entry(key, entry_id, fields)
        conn.send(f"${len(added_entry_id)}\r\n{added_entry_id}\r\n".encode())

    def handle_info_command(self, conn, command):
        """
        Handle the INFO command and return the replication information.
        """
        if len(command) > 1 and command[1].lower() == "replication":
            # Build the replication information response
            response_lines = [
                f"role:{self.role}",
                f"master_replid:{self.master_replid}",
                f"master_repl_offset:{self.master_repl_offset}"
            ]
            response = "\r\n".join(response_lines)
            conn.send(f"${len(response)}\r\n{response}\r\n".encode())
        else:
            conn.send(b"$-1\r\n")

def main():
    parser = argparse.ArgumentParser(description="Redis-like server")
    parser.add_argument("--port", type=int, default=6379, help="Port to start the server on (default: 6379)")
    parser.add_argument("--replicaof", nargs="+", metavar=('MASTER_HOST', 'MASTER_PORT'), help="Specify the master host and port for replication (e.g., 'localhost 6379')")
    args = parser.parse_args()

    # Determine the role of the server
    role = "slave" if args.replicaof else "master"
    
    # Create and start the server
    server = RedisServer(port=args.port, role=role)
    server.start()

if __name__ == "__main__":
    main()
