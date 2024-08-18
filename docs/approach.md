## 1. Start with the Basics
We starts with basic stages like binding to a port and responding to PING commands. 
This aligns with the initial steps such as setting up a TCP server and handling simple commands.

Binding to a Port: We have to make sure our server can bind to a specific port and handle incoming client connections.
Responding to PING: We will implement basic command handling where the server responds with "PONG" when receiving the PING command.



Stage 1: Bind to a port. 
Stage 2: Give Pong
Stage 3: A Redis server starts to listen for the next command as soon as it's done responding to the previous one. This allows Redis clients to send multiple commands using the same connection.

Stage 4: 
In this stage, we'll add support for multiple concurrent clients.

In addition to handling multiple commands from the same client, Redis servers are also designed to handle multiple clients at once.

To implement this, we'll need to either use threads, or, if we're feeling adventurous, an Event Loop (like the official Redis implementation does).

These two will be sent concurrently so that we test wer server's ability to handle concurrent clients.
$ redis-cli PING
$ redis-cli PING


Stage 5: In this stage, we'll add support for the ECHO command.

ECHO is a command like PING that's used for testing and debugging. It accepts a single argument and returns it back as a RESP bulk string.

$ redis-cli PING # The command we implemented in previous stages PONG $ redis-cli ECHO hey # The command we'll implement in this stage hey We suggest that we implement a proper Redis protocol parser in this stage. It'll come in handy in later stages. Redis command names are case-insensitive, so ECHO, echo and EcHo are all valid commands. The tester will send a random string as an argument to the ECHO command, so we won't be able to hardcode the response to pass this stage. The exact bytes wer program will receive won't be just ECHO hey, we'll receive something like this: *2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n. That's ["ECHO", "hey"] encoded using the Redis protocol. (https://redis.io/docs/latest/develop/reference/protocol-spec/) we can read more about how "commands" are handled in the Redis protocol here. (https://redis.io/docs/latest/develop/reference/protocol-spec/#sending-commands-to-a-redis-server)

"Clients send commands to a Redis server as an array of bulk strings. The first (and sometimes also the second) bulk string in the array is the command's name. Subsequent elements of the array are the arguments for the command."

"The server replies with a RESP type. The reply's type is determined by the command's implementation and possibly by the client's protocol version."


Stage 6: SET AND GET

In this stage, we'll add support for the SET & GET commands.

The SET command is used to set a key to a value. The GET command is used to retrieve the value of a key.

$ redis-cli SET foo bar
OK
$ redis-cli GET foo
bar
The SET command supports a number of extra options like EX (expiry time in seconds), PX (expiry time in milliseconds) and more. We won't cover these extra options in this stage. We'll get to them in later stages.


Just like the previous stage, the values used for keys and values will be random, so we won't be able to hardcode the response to pass this stage.
If a key doesn't exist, the GET command should return a "null bulk string" ($-1\r\n). We won't explicitly test this in this stage, but we'll need it for the next stage (expiry).

Stage 7: Expiry
In this stage, we'll add support for setting a key with an expiry.

The expiry for a key can be provided using the "PX" argument to the SET command. The expiry is provided in milliseconds.

$ redis-cli SET foo bar px 100 # Sets the key "foo" to "bar" with an expiry of 100 milliseconds
OK
After the key has expired, a GET command for that key should return a "null bulk string" ($-1\r\n).


Just like command names, command arguments are also case-insensitive. So PX, px and pX are all valid.
The keys, values and expiry times used in the tests will be random, so we won't be able to hardcode a response to pass this stage.

https://redis.io/docs/latest/commands/set/


Stage - 8: Code Refactoring
To clean up the code and make it more Pythonic according to clean code standards, we have to follow these steps:

Modularize the code: Break the code into smaller, reusable functions and classes.
Use context managers: Handle socket connections and client sessions using context managers.
Separate responsibilities: Split the code into separate classes and methods to follow the single responsibility principle.
Improve readability: Add comments and docstrings where necessary, and refactor variable names for clarity.


Stage-9: RDB Persistence
In this stage, we'll add support for two configuration parameters related to RDB persistence, as well as the CONFIG GET command.

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

we don't need to read the RDB file in this stage, we only need to store dir and dbfilename. Reading from the file will be covered in later stages.


Stage - 10
we can remove persistence logic now and go back to stage-8 code to maintain simplicity

In this stage, we'll add support for the TYPE command.

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

For now, we only need to handle the "string" and "none" types. We'll add support for the "stream" type in the next stage.

Stage-11
In this stage, we'll add support for creating a Redis stream using the XADD command.
https://redis.io/docs/latest/develop/data-types/streams/
Redis Streams & Entries
Streams are one of the data types that Redis supports. A stream is identified by a key, and it contains multiple entries.

Each entry consists of one or more key-value pairs, and is assigned a unique ID.

For example, if we were using a Redis stream to store real-time data from a temperature & humidity monitor, the contents of the stream might look like this:

entries:
  - id: 1526985054069-0 # (ID of the first entry)
    temperature: 36 # (A key value pair in the first entry)
    humidity: 95 # (Another key value pair in the first entry)

  - id: 1526985054079-0 # (ID of the second entry)
    temperature: 37 # (A key value pair in the first entry)
    humidity: 94 # (Another key value pair in the first entry)

  # ... (and so on)
We'll take a closer look at the format of entry IDs (1526985054069-0 and 1526985054079-0 in the example above) in the upcoming stages.

The XADD command
The XADD command appends an entry to a stream. If a stream doesn't exist already, it is created.

Here's how it works:

$ redis-cli XADD stream_key 1526919030474-0 temperature 36 humidity 95
"1526919030474-0" # (ID of the entry created)
The return value is the ID of the entry created, encoded as a bulk string.

XADD supports other optional arguments, but we won't deal with them in this challenge.

XADD also supports auto-generating entry IDs. We'll add support for that in later stages. For now, we'll only deal with explicit IDs (like 1526919030474-0 in the example above).

 
$ redis-cli XADD stream_key 0-1 foo bar
"0-1"

Server should respond with $3\r\n0-1\r\n, which is 0-1 encoded as a RESP bulk string.


$ redis-cli TYPE stream_key
"stream"
Server should respond with +stream\r\n, which is stream encoded as a RESP simple string.

 
we still need to handle the "string" and "none" return values for the TYPE command. "stream" should only be returned for keys that are streams.

Stage-12 : Replication: Info command
In this extension, you'll extend your Redis server to support leader-follower replication. You'll be able to run multiple Redis servers with one acting as the "master" and the others as "replicas". Changes made to the master will be automatically replicated to replicas.

Since we'll need to run multiple instances of your Redis server at once, we can't run all of them on port 6379.

In this stage, we'll add support for starting the Redis server on a custom port. The port number will be passed to your program via the --port flag.

The INFO command returns information and statistics about a Redis server. In this stage, we'll add support for the replication section of the INFO command.

The replication section
When you run the INFO command against a Redis server, you'll see something like this:

$ redis-cli INFO replication
# Replication
role:master
connected_slaves:0
master_replid:8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:
The reply to this command is a Bulk string where each line is a key value pair, separated by ":".

Here are what some of the important fields mean:

role: The role of the server (master or slave)
connected_slaves: The number of connected replicas
master_replid: The replication ID of the master (we'll get to this in later stages)
master_repl_offset: The replication offset of the master (we'll get to this in later stages)
In this stage, you'll only need to support the role key. We'll add support for other keys in later stages.
 
 
 
In the response for the INFO command, only need to support the role key for this stage. We'll add support for the other keys in later stages.
The # Replication heading in the response is optional, you can ignore it.
The response to INFO needs to be encoded as a Bulk string.
An example valid response would be $11\r\nrole:master\r\n (the string role:master encoded as a Bulk string)
 
