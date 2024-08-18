import unittest
import socket
import threading
import time
 
from networking.server import main  

class TestRedisServer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # we are starting the server in a separate thread before running the tests
        cls.server_thread = threading.Thread(target=main)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        # Wait for the server to start
        time.sleep(1)

    def create_client(self):
        """Helper function to create a client connection to the server."""
        client = socket.create_connection(("localhost", 6380))
        return client

    def send_command(self, client, command):
        """Helper function to send a command and receive the response."""
        client.sendall(command.encode())
        return client.recv(1024).decode()

    def test_ping_command(self):
        client = self.create_client()
        response = self.send_command(client, "*1\r\n$4\r\nPING\r\n")
        self.assertEqual(response, "+PONG\r\n")
        client.close()

    def test_echo_command(self):
        client = self.create_client()
        response = self.send_command(client, "*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n")
        self.assertEqual(response, "$3\r\nhey\r\n")
        client.close()

    def test_set_get_command(self):
        client = self.create_client()

        # Test SET command
        response = self.send_command(client, "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n")
        self.assertEqual(response, "+OK\r\n")

        # Test GET command (existing key)
        response = self.send_command(client, "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n")
        self.assertEqual(response, "$3\r\nbar\r\n")

        # Test GET command (non-existing key)
        response = self.send_command(client, "*2\r\n$3\r\nGET\r\n$12\r\nnonexistent\r\n")
        self.assertEqual(response, "$-1\r\n")

        client.close()

    def test_multiple_set_get(self):
        client = self.create_client()   

        # Set multiple keys
        self.send_command(client, "*3\r\n$3\r\nSET\r\n$3\r\nkey1\r\n$6\r\nvalue1\r\n")
        self.send_command(client, "*3\r\n$3\r\nSET\r\n$3\r\nkey2\r\n$6\r\nvalue2\r\n")

        # Retrieve the values
        response = self.send_command(client, "*2\r\n$3\r\nGET\r\n$4\r\nkey1\r\n")
        self.assertEqual(response, "$6\r\nvalue1\r\n")  # 

        response = self.send_command(client, "*2\r\n$3\r\nGET\r\n$4\r\nkey2\r\n")
        self.assertEqual(response, "$6\r\nvalue2\r\n")   

        client.close()

    def test_overwrite_set(self):
        client = self.create_client()

        # Set a key
        self.send_command(client, "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n")
        
        # Overwrite the same key
        response = self.send_command(client, "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$6\r\nfoobar\r\n")
        self.assertEqual(response, "+OK\r\n")

        # Retrieve the updated value
        response = self.send_command(client, "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n")
        self.assertEqual(response, "$6\r\nfoobar\r\n")

        client.close()

    def test_get_nonexistent_key(self):
        client = self.create_client()

        # Try to get a key that doesn't exist
        response = self.send_command(client, "*2\r\n$3\r\nGET\r\n$7\r\nunknown\r\n")
        self.assertEqual(response, "$-1\r\n")

        client.close()

if __name__ == "__main__":
    unittest.main()
