import selectors
import socket

# Initialize the default selector (automatically chooses the best available)
sel = selectors.DefaultSelector()

def accept(sock):
    # Accept a new client connection
    client_socket, addr = sock.accept()
    print(f"New connection from {addr}")
    
    # Set the client socket to non-blocking mode
    client_socket.setblocking(False)
    
    # Register the client socket to be monitored for read events
    sel.register(client_socket, selectors.EVENT_READ, read)

def read(client_socket):
    try:
        # Read data from the client socket
        data = client_socket.recv(1024)
        if data:
            print(f"Received {data.decode().strip()} from {client_socket.getpeername()}")
            
            # If data is received, change the socket to monitor for write events
            sel.modify(client_socket, selectors.EVENT_WRITE, write)
        else:
            # If no data is received, it means the client closed the connection
            print(f"Client {client_socket.getpeername()} closed the connection")
            sel.unregister(client_socket)
            client_socket.close()
    except Exception as e:
        # If an exception occurs (e.g., connection reset), handle it and close the connection
        print(f"Error reading from {client_socket.getpeername()}: {e}")
        sel.unregister(client_socket)
        client_socket.close()

def write(client_socket):
    try:
        # Send a response back to the client
        message = "Echo from server\n".encode()
        client_socket.send(message)
        print(f"Sent echo message to {client_socket.getpeername()}")
        
        # After writing, change the socket back to monitor for read events
        sel.modify(client_socket, selectors.EVENT_READ, read)
    except Exception as e:
        # Handle any exceptions during writing
        print(f"Error writing to {client_socket.getpeername()}: {e}")
        sel.unregister(client_socket)
        client_socket.close()

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(100)
server_socket.setblocking(False)

# Register the server socket to be monitored for incoming connections (read events)
sel.register(server_socket, selectors.EVENT_READ, accept)
print("Server started on localhost:12345. Waiting for connections...")

# Main event loop
while True:
    # Use select() to wait for any registered socket to be ready
    events = sel.select()
    print(events)
    
    # Process each ready socket
    for key, mask in events:
        # Retrieve the callback function associated with the socket
        callback = key.data
        print(key.data)
        print(f"Event triggered on {key.fileobj.getpeername() if key.fileobj != server_socket else 'server socket'}")
        
        # Call the callback function (accept, read, or write)
        callback(key.fileobj)
