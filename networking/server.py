import socket
import threading
import time

# In-memory store for key-value pairs and their expiration times
store = {}
expiration_store = {}

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
    global store, expiration_store
    try:
        while True:
            request: bytes = conn.recv(512)
            print(request)
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
            elif cmd_name == "set":
                key, value = command[1], command[2]
                expiration_time = None
                if len(command) >= 5 and command[3].lower() == "px":
                    try:
                        expiration_time = int(command[4])
                    except ValueError:
                        conn.send(b"-ERR invalid expiration time\r\n")
                        continue
                
                store[key] = value
                if expiration_time:
                    # Store expiration time in milliseconds
                    expiration_store[key] = time.time() * 1000 + expiration_time  
                conn.send(b"+OK\r\n")
            elif cmd_name == "get":
                key = command[1]
                if key in expiration_store:
                    current_time = time.time() * 1000
                    if current_time >= expiration_store[key]:
                        # Key has expired
                        del store[key]
                        del expiration_store[key]
                        conn.send(b"$-1\r\n")
                        continue
                
                value = store.get(key)
                if value is None:
                    conn.send(b"$-1\r\n")
                else:
                    resp_message = f"${len(value)}\r\n{value}\r\n"
                    conn.send(resp_message.encode())
    except ConnectionResetError:
        pass
    finally:
        conn.close()  

def main():
    print("Logs will appear here")

    server_socket = socket.create_server(("localhost", 6380), reuse_port=True)
    server_socket.listen()

    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
    finally:
        # Ensure the server socket is closed on exit
        server_socket.close()  


if __name__ == "__main__":
    main()
