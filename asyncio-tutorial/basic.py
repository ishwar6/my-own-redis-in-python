import asyncio

async def do_io():
    print("io start")
    await asyncio.sleep(2)
    print("io ends")


async def do_something_else():
    print("doing something else")



def main() -> None:
    loop  = asyncio.get_event_loop()
    loop.run_until_complete(do_io())
    loop.run_until_complete(do_something_else())
    loop.close()


if __name__ == "__main__":
    main()

# Sequential Execution:
# The loop.run_until_complete(do_io()) method runs the do_io() coroutine and waits for it to complete before returning control to the next line.
# After do_io() finishes, the next line, loop.run_until_complete(do_something_else()), is executed.
# This means the two coroutines are executed sequentially, one after the other, not concurrently.


