import socket
import unittest
import time

class TestRedisServer(unittest.TestCase):
    def setUp(self):
        # Setup client connection to the Redis-like server
        self.client = socket.create_connection(("localhost", 6380))

    def tearDown(self):
        # Close the client connection after each test
        self.client.close()

    def send_command(self, command: str):
        """
        Send a Redis command to the server and receive the response.
        """
        self.client.sendall(command.encode())
        return self.client.recv(1024).decode()

    def test_ping_command(self):
        # Test PING command
        response = self.send_command("*1\r\n$4\r\nPING\r\n")
        self.assertEqual(response, "+PONG\r\n")

    def test_echo_command(self):
        # Test ECHO command
        response = self.send_command("*2\r\n$4\r\nECHO\r\n$5\r\napple\r\n")
        self.assertEqual(response, "$5\r\napple\r\n")

    def test_set_get_command(self):
        # Test SET and GET commands
        self.send_command("*3\r\n$3\r\nSET\r\n$9\r\nraspberry\r\n$10\r\nstrawberry\r\n")
        set_response = self.send_command("*2\r\n$3\r\nGET\r\n$9\r\nraspberry\r\n")
        self.assertEqual(set_response, "$10\r\nstrawberry\r\n")

    def test_key_expiry(self):
        # Test SET with PX option for key expiry and check if it expires
        self.send_command("*5\r\n$3\r\nSET\r\n$9\r\nraspberry\r\n$6\r\nbanana\r\n$2\r\nPX\r\n$3\r\n100\r\n")
        time.sleep(0.2)  # Sleep for 200ms to ensure the key expires
        get_response = self.send_command("*2\r\n$3\r\nGET\r\n$9\r\nraspberry\r\n")
        self.assertEqual(get_response, "$-1\r\n")  # Key should have expired

    def test_config_get_dir(self):
        # Test CONFIG GET dir command
        response = self.send_command("*3\r\n$6\r\nCONFIG\r\n$3\r\nGET\r\n$3\r\ndir\r\n")
        self.assertIn("/tmp", response)  # The default directory is /tmp/redis-data or as provided

    def test_config_get_dbfilename(self):
        # Test CONFIG GET dbfilename command
        response = self.send_command("*3\r\n$6\r\nCONFIG\r\n$3\r\nGET\r\n$10\r\ndbfilename\r\n")
        self.assertIn("rdbfile", response)  # The default dbfilename is "rdbfile" or as provided

if __name__ == "__main__":
    unittest.main()
