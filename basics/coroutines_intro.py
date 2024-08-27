# import asyncio


# async def add_one(number: int) -> int:
#     return number + 1

# async def main() -> None:
#     one_plus_one = await add_one(1)
#     two_plus_one = await add_one(2)
#     print(one_plus_one)
#     print(two_plus_one)
    
    
# asyncio.run(main())



import asyncio


async def delay(delay_seconds: int) -> int:
    print(f'sleeping for {delay_seconds} second(s)')
    await asyncio.sleep(delay_seconds)
    print(f'finished sleeping for {delay_seconds} second(s)')
    return delay_seconds

# async def add_one(number: int) -> int:
#     return number + 1

# async def hello_world_message() -> str:
#     await delay(1)
#     return "Hello World!"

# async def main() -> None:
#     message = await hello_world_message()
#     one_plus_one = await add_one(1)
#     print(one_plus_one)
#     print(message)


# async def main():
#     sleep_for_three = asyncio.create_task(delay(3))
#     sleep_again = asyncio.create_task(delay(3))
#     sleep_once_more = asyncio.create_task(delay(3))
#     await sleep_for_three
#     await sleep_again
#     await sleep_once_more

# asyncio.run(main())


async def hello_every_second():
    for i in range(2):
        await asyncio.sleep(1)
        print("I'm running other code while I'm waiting!")

async def main():
    first_delay = asyncio.create_task(delay(3))
    second_delay = asyncio.create_task(delay(3))

    await hello_every_second()
    await first_delay
    await second_delay

asyncio.run(main())