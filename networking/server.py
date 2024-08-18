import socket
import threading

# In-memory store for key-value pairs
store = {}

def parse_resp(data: str):
    """
    Parse a RESP-formatted command.
    """
    lines = data.split("\r\n")
    if len(lines) < 3:
        return None

    # The command starts with an array indicator
    if lines[0].startswith("*"):
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
        return elements
    return None

def handle_client(conn, addr):
    # we are storing key value pair here. 
    global store 
    while True:
        try:
            request: bytes = conn.recv(512)
            if not request:
                break

            data: str = request.decode()
            command = parse_resp(data)
            if not command:
                continue
            
            cmd_name = command[0].lower()
            
            if cmd_name == "ping":
                conn.send(b"+PONG\r\n")
            elif cmd_name == "echo" and len(command) > 1:
                message = command[1]
                resp_message = f"${len(message)}\r\n{message}\r\n"
                conn.send(resp_message.encode())
            elif cmd_name == "set" and len(command) == 3:
                key, value = command[1], command[2]
                store[key] = value
                conn.send(b"+OK\r\n")
            elif cmd_name == "get" and len(command) == 2:
                key = command[1]
                value = store.get(key)
                if value is None:
                    conn.send(b"$-1\r\n")
                else:
                    resp_message = f"${len(value)}\r\n{value}\r\n"
                    conn.send(resp_message.encode())
        except ConnectionResetError:
            break
    
def main():
    print("Logs will appear here")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()


if __name__ == "__main__":
    main()
