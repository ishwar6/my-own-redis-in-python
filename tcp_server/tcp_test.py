import threading
import time
import subprocess

# Import server and client modules
import tcp_server
import tcp_client

def run_server():
    tcp_server.start_server()

def run_client():
    tcp_client.start_client()

if __name__ == "__main__":
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    # Run the client
    run_client()
    
    # Give the server a moment to handle the client before finishing
    time.sleep(1)
