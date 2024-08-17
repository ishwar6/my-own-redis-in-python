import asyncio
import socket
import pytest

# Test function to connect to the Redis server and check for the welcome message
@pytest.mark.asyncio
async def test_server_connection():
    # Create a TCP socket
    reader, writer = await asyncio.open_connection('127.0.0.1', 6370)

    # Read the welcome message from the server
    data = await reader.read(100)
    message = data.decode()

    # Assert that the message is correct
    assert message == "Connected to Redis-like server\r\n"

    # Close the connection
    writer.close()
    await writer.wait_closed()

# Running the server in background for testing
from .networking.server import RedisServer

@pytest.fixture(scope="module", autouse=True)
def start_server():
    redis_server = RedisServer()
    asyncio.run(redis_server.main())
