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


Stage 5: In this stage, you'll add support for the ECHO command.

ECHO is a command like PING that's used for testing and debugging. It accepts a single argument and returns it back as a RESP bulk string.

$ redis-cli PING # The command you implemented in previous stages PONG $ redis-cli ECHO hey # The command you'll implement in this stage hey We suggest that you implement a proper Redis protocol parser in this stage. It'll come in handy in later stages. Redis command names are case-insensitive, so ECHO, echo and EcHo are all valid commands. The tester will send a random string as an argument to the ECHO command, so you won't be able to hardcode the response to pass this stage. The exact bytes your program will receive won't be just ECHO hey, you'll receive something like this: *2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n. That's ["ECHO", "hey"] encoded using the Redis protocol. (https://redis.io/docs/latest/develop/reference/protocol-spec/) You can read more about how "commands" are handled in the Redis protocol here. (https://redis.io/docs/latest/develop/reference/protocol-spec/#sending-commands-to-a-redis-server)

"Clients send commands to a Redis server as an array of bulk strings. The first (and sometimes also the second) bulk string in the array is the command's name. Subsequent elements of the array are the arguments for the command."

"The server replies with a RESP type. The reply's type is determined by the command's implementation and possibly by the client's protocol version."


Stage 6: SET AND GET

In this stage, you'll add support for the SET & GET commands.

The SET command is used to set a key to a value. The GET command is used to retrieve the value of a key.

$ redis-cli SET foo bar
OK
$ redis-cli GET foo
bar
The SET command supports a number of extra options like EX (expiry time in seconds), PX (expiry time in milliseconds) and more. We won't cover these extra options in this stage. We'll get to them in later stages.


Just like the previous stage, the values used for keys and values will be random, so you won't be able to hardcode the response to pass this stage.
If a key doesn't exist, the GET command should return a "null bulk string" ($-1\r\n). We won't explicitly test this in this stage, but you'll need it for the next stage (expiry).

Stage 7: Expiry
In this stage, you'll add support for setting a key with an expiry.

The expiry for a key can be provided using the "PX" argument to the SET command. The expiry is provided in milliseconds.

$ redis-cli SET foo bar px 100 # Sets the key "foo" to "bar" with an expiry of 100 milliseconds
OK
After the key has expired, a GET command for that key should return a "null bulk string" ($-1\r\n).


Just like command names, command arguments are also case-insensitive. So PX, px and pX are all valid.
The keys, values and expiry times used in the tests will be random, so you won't be able to hardcode a response to pass this stage.

https://redis.io/docs/latest/commands/set/


Stage - 8: Code Refactoring
To clean up the code and make it more Pythonic according to clean code standards, we have to follow these steps:

Modularize the code: Break the code into smaller, reusable functions and classes.
Use context managers: Handle socket connections and client sessions using context managers.
Separate responsibilities: Split the code into separate classes and methods to follow the single responsibility principle.
Improve readability: Add comments and docstrings where necessary, and refactor variable names for clarity.


Stage-9: RDB Persistence
In this stage, you'll add support for two configuration parameters related to RDB persistence, as well as the CONFIG GET command.

RDB files
An RDB file is a point-in-time snapshot of a Redis dataset. When RDB persistence is enabled, the Redis server syncs its in-memory state with an RDB file, by doing the following:

On startup, the Redis server loads the data from the RDB file.
While running, the Redis server periodically takes new snapshots of the dataset, in order to update the RDB file.
dir and dbfilename
The configuration parameters dir and dbfilename specify where an RDB file is stored:

dir - the path to the directory where the RDB file is stored (example: /tmp/redis-data)
dbfilename - the name of the RDB file (example: rdbfile)
The CONFIG GET command
The CONFIG GET command returns the values of configuration parameters.

It takes in one or more configuration parameters and returns a RESP array of key-value pairs:

$ redis-cli CONFIG GET dir
1) "dir"
2) "/tmp/redis-data"
Although CONFIG GET can fetch multiple parameters at a time, the tester will only send CONFIG GET commands with one parameter at a time.

You don't need to read the RDB file in this stage, you only need to store dir and dbfilename. Reading from the file will be covered in later stages.


Stage - 10
You can remove persistence logic now and go back to stage-8 code to maintain simplicity

In this stage, you'll add support for the TYPE command.

The TYPE command
The TYPE command returns the type of value stored at a given key.

It returns one of the following types: string, list, set, zset, hash, and stream.

Here's how it works:

$ redis-cli SET some_key foo
"OK"
$ redis-cli TYPE some_key
"string"
If a key doesn't exist, the return value will be "none".

$ redis-cli TYPE missing_key
"none"
The return value is encoded as a simple string 
https://redis.io/docs/latest/develop/reference/protocol-spec/#simple-strings

For now, you only need to handle the "string" and "none" types. We'll add support for the "stream" type in the next stage.

