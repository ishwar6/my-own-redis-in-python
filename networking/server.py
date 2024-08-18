import socket
import threading

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


def test_parse_resp():
    # Test case 1: Simple PING command
    data = "*1\r\n$4\r\nPING\r\n"
    assert parse_resp(data) == ["PING"]

    # Test case 2: ECHO command with a single argument
    data = "*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n"
    assert parse_resp(data) == ["ECHO", "hey"]

    # Test case 3: ECHO command with multiple arguments
    data = "*3\r\n$4\r\nECHO\r\n$5\r\nhello\r\n$5\r\nworld\r\n"
    assert parse_resp(data) == ["ECHO", "hello", "world"]

    # Test case 4: Empty input (invalid)
    data = ""
    assert parse_resp(data) is None

    # Test case 5: Incorrect RESP format
    data = "*1\r\n$4\r\nINCORRECT_FORMAT\r\n"
    assert parse_resp(data) == ["INCORRECT_FORMAT"]

    print("All tests passed!")


# Run the tests
test_parse_resp()
