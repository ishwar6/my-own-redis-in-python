import socket
import threading
import time

# Function to handle a single client connection
def client_task(id, message, delay=0):
    # Add a delay to simulate staggered client connections
    time.sleep(delay)
    
    # Create a socket and connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 12345))
        print(f"Client {id} connected to the server")
        
        # Send a message to the server
        client_socket.sendall(message.encode())
        print(f"Client {id} sent: {message}")
        
        # Receive the response from the server
        response = client_socket.recv(1024)
        print(f"Client {id} received: {response.decode().strip()}")

# Number of client connections to simulate
num_clients = 5

# List to hold client threads
client_threads = []

# Create and start multiple client threads
for i in range(num_clients):
    # Each client will send a unique message
    message = f"Hello from client {i + 1}"
    
    # Start a new thread for each client
    thread = threading.Thread(target=client_task, args=(i + 1, message, i * 0.5))  # Add a slight delay between connections
    thread.start()
    client_threads.append(thread)

# Wait for all client threads to complete
for thread in client_threads:
    thread.join()

print("All clients have finished.")
