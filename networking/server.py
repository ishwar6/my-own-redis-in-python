import socket
import threading

def handle_client(conn, addr):
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Handling connection from {addr}")

    pong = "+PONG\r\n"

    while True:
        try:
            # Receiving data from the client
            request: bytes = conn.recv(512)
            if not request:
                print(f"[{thread_name}] No data received. Closing connection with {addr}")
                break  # Client closed the connection

            data: str = request.decode()
            print(f"[{thread_name}] Received data: {data.strip()} from {addr}")

            # Respond to "PING"
            if "ping" in data.lower():
                print(f"[{thread_name}] Sending PONG to {addr}")
                conn.send(pong.encode())
        except ConnectionResetError:
            print(f"[{thread_name}] Connection reset by {addr}")
            break

    print(f"[{thread_name}] Connection with {addr} closed")
    conn.close()

def main():
    print("Server started and listening for connections")

    server_socket = socket.create_server(("localhost", 6380), reuse_port=True)
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        print(f"[Main Thread] Accepted connection from {addr}")

        # Start a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True  # This ensures threads are cleaned up on exit
        print(f"[Main Thread] Starting thread {client_thread.name} for {addr}")
        client_thread.start()

if __name__ == "__main__":
    main()


# Server started and listening for connections
# [Main Thread] Accepted connection from ('127.0.0.1', 54651)
# [Main Thread] Starting thread Thread-1 (handle_client) for ('127.0.0.1', 54651)
# [Thread-1 (handle_client)] Handling connection from ('127.0.0.1', 54651)
# [Thread-1 (handle_client)] Received data: PING from ('127.0.0.1', 54651)
# [Thread-1 (handle_client)] Sending PONG to ('127.0.0.1', 54651)
# [Main Thread] Accepted connection from ('127.0.0.1', 54652)
# [Main Thread] Starting thread Thread-2 (handle_client) for ('127.0.0.1', 54652)
# [Thread-1 (handle_client)] No data received. Closing connection with ('127.0.0.1', 54651)
# [Thread-1 (handle_client)] Connection with ('127.0.0.1', 54651) closed
# [Thread-2 (handle_client)] Handling connection from ('127.0.0.1', 54652)
# [Main Thread] Accepted connection from ('127.0.0.1', 54653)
# [Main Thread] Starting thread Thread-3 (handle_client) for ('127.0.0.1', 54653)
# [Thread-2 (handle_client)] Received data: PING from ('127.0.0.1', 54652)
# [Thread-3 (handle_client)] Handling connection from ('127.0.0.1', 54653)
# [Thread-2 (handle_client)] Sending PONG to ('127.0.0.1', 54652)
# [Main Thread] Accepted connection from ('127.0.0.1', 54654)
# [Thread-3 (handle_client)] Received data: PING from ('127.0.0.1', 54653)
# [Thread-3 (handle_client)] Sending PONG to ('127.0.0.1', 54653)
# [Main Thread] Starting thread Thread-4 (handle_client) for ('127.0.0.1', 54654)
# [Thread-2 (handle_client)] No data received. Closing connection with ('127.0.0.1', 54652)
# [Thread-2 (handle_client)] Connection with ('127.0.0.1', 54652) closed
# [Thread-4 (handle_client)] Handling connection from ('127.0.0.1', 54654)
# [Thread-4 (handle_client)] Received data: PING from ('127.0.0.1', 54654)
# [Thread-4 (handle_client)] Sending PONG to ('127.0.0.1', 54654)
# [Thread-3 (handle_client)] No data received. Closing connection with ('127.0.0.1', 54653)
# [Thread-3 (handle_client)] Connection with ('127.0.0.1', 54653) closed
# [Thread-4 (handle_client)] No data received. Closing connection with ('127.0.0.1', 54654)
# [Thread-4 (handle_client)] Connection with ('127.0.0.1', 54654) closed