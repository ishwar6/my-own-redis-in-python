import socket

# Server configuration
SERVER_ADDRESS = ('localhost', 8888)
REQUEST_QUEUE_SIZE = 5

def handle_client(client_connection):
    request_data = client_connection.recv(1024)
    print(f"Received data from our client: {request_data.decode()}")
    
    # Send a simple response back to the client
    response = b"HTTP/1.1 200 OK\n\nHello, World!"
    client_connection.sendall(response)
    
    # Close the connection
    client_connection.close()

def start_server():
    # Create a TCP/IP socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow the reuse of the address
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the server address
    listen_socket.bind(SERVER_ADDRESS)
    
    # Start listening for incoming connections
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print(f"Server listening on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
    
    while True:
        # Accept a new connection
        client_connection, client_address = listen_socket.accept()
        print(f"New connection from {client_address}")
        
        # Handle the client connection
        handle_client(client_connection)

if __name__ == "__main__":
    start_server()
