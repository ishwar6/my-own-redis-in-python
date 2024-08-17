import sys
import os
import asyncio
import pytest
import socket

# Add the project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from networking.server import RedisServer

@pytest.fixture(scope="module", autouse=True)
def start_server():
    # Run the server in the background
    loop = asyncio.get_event_loop()
    server_task = loop.create_task(RedisServer().main())
    yield  # This yields control back to the test
    server_task.cancel()  # Stop the server after the test completes

@pytest.mark.asyncio
async def test_server_connection():
    # Allow the server some time to start up
    await asyncio.sleep(1)

    # Create a TCP socket to connect to the server
    reader, writer = await asyncio.open_connection('127.0.0.1', 6379)

    # Read the welcome message from the server
    data = await reader.read(100)
    message = data.decode()

    # Assert that the message is correct
    assert message == "Connected to Redis-like server\r\n"

    # Close the connection
    writer.close()
    await writer.wait_closed()
