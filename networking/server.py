#  Lets start by implementing the networking and basic command-handling logic, 
# which includes binding to a port, handling concurrent clients, and processing simple commands like PING, ECHO, SET, and GET.

import asyncio
from commands.commands import CommandHandler

class RedisServer:
    def __init__(self):
        self.command_handler = CommandHandler()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Connected by {addr}")

        while True:
            data = await reader.read(1024)
            if not data:
                break

            command = data.decode().strip()
            print(f"Received command: {command} from {addr}")

            response = self.command_handler.handle(command)
            writer.write(response.encode())
            await writer.drain()

        print(f"Connection closed by {addr}")
        writer.close()

    async def main(self):
        server = await asyncio.start_server(self.handle_client, '127.0.0.1', 6379)
        async with server:
            print("Server started on port 6379")
            await server.serve_forever()

if __name__ == '__main__':
    redis_server = RedisServer()
    asyncio.run(redis_server.main())
