import socket
import threading

def client_task(client_id, host='localhost', port=6380):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"[Client {client_id}] Connected to the server")

        # Send PING command
        s.sendall(b"PING\r\n")
        print(f"[Client {client_id}] Sent PING")

        # Receive the response
        response = s.recv(1024).decode()
        print(f"[Client {client_id}] Received: {response.strip()}")

def run_concurrent_clients(num_clients):
    threads = []

    for i in range(num_clients):
        client_thread = threading.Thread(target=client_task, args=(i,))
        threads.append(client_thread)
        client_thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    number_of_clients = 4  # You can change this number to simulate more or fewer clients
    run_concurrent_clients(number_of_clients)
