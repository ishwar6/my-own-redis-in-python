## 1. Start with the Basics
We starts with basic stages like binding to a port and responding to PING commands. 
This aligns with the initial steps such as setting up a TCP server and handling simple commands.

Binding to a Port: We have to make sure our server can bind to a specific port and handle incoming client connections.
Responding to PING: We will implement basic command handling where the server responds with "PONG" when receiving the PING command.



Stage 1: Bind to a port. 
Stage 2: Give Pong
Stage 3: A Redis server starts to listen for the next command as soon as it's done responding to the previous one. This allows Redis clients to send multiple commands using the same connection.

Stage 4: 
In this stage, you'll add support for multiple concurrent clients.

In addition to handling multiple commands from the same client, Redis servers are also designed to handle multiple clients at once.

To implement this, you'll need to either use threads, or, if you're feeling adventurous, an Event Loop (like the official Redis implementation does).

These two will be sent concurrently so that we test your server's ability to handle concurrent clients.
$ redis-cli PING
$ redis-cli PING


Stage 5: 
In this stage, you'll add support for the ECHO command.

ECHO is a command like PING that's used for testing and debugging. It accepts a single argument and returns it back as a RESP bulk string.

$ redis-cli PING # The command you implemented in previous stages
PONG
$ redis-cli ECHO hey # The command you'll implement in this stage
hey
We suggest that you implement a proper Redis protocol parser in this stage. It'll come in handy in later stages.
Redis command names are case-insensitive, so ECHO, echo and EcHo are all valid commands.
The tester will send a random string as an argument to the ECHO command, so you won't be able to hardcode the response to pass this stage.
The exact bytes your program will receive won't be just ECHO hey, you'll receive something like this: *2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n. That's ["ECHO", "hey"] encoded using the Redis protocol.
(https://redis.io/docs/latest/develop/reference/protocol-spec/)
You can read more about how "commands" are handled in the Redis protocol here. (https://redis.io/docs/latest/develop/reference/protocol-spec/#sending-commands-to-a-redis-server)

"Clients send commands to a Redis server as an array of bulk strings. The first (and sometimes also the second) bulk string in the array is the command's name. Subsequent elements of the array are the arguments for the command."

"The server replies with a RESP type. The reply's type is determined by the command's implementation and possibly by the client's protocol version."


