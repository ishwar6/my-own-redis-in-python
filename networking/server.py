import socket
def main():
    print("Logs will appear here")

    pong = "+PONG\r\n"

    server_socket = socket.create_server(("localhost", 6379),   reuse_port=True)
    conn, addr = server_socket.accept()
    while True:
        request: bytes = conn.recv(512)
        data:str = request.decode()
        if "ping" in data.lower():
            conn.send("+PONG\r\n".encode())


if __name__ == "__main__":
    main()