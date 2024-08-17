import socket

def start_client():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server
    server_address = ('localhost', 8888)
    sock.connect(server_address)
    
    try:
        # Send data
        message = b'test'
        sock.sendall(message)
        
        # Receive a response
        data = sock.recv(1024)
        print(f"CLIENT: Received response from the server: {data.decode()}")
    finally:
        # Close the socket
        sock.close()

if __name__ == "__main__":
    start_client()
