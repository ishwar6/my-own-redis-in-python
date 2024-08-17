import asyncio

async def client_task():
    reader, writer = await asyncio.open_connection('127.0.0.1', 3100)

    writer.write(b"Hello, Server")
    await writer.drain()

    response = await reader.read(1024)
    print(f"Client received: {response.decode('utf-8')}")

    writer.close()
    await writer.wait_closed()

async def main():
    tasks = [client_task() for _ in range(5)]  # Number of clients
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
