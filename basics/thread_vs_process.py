import threading

# Function that will run in a separate thread
def print_numbers():
    current_thread = threading.current_thread()
    for i in range(5):
        print(f"Thread ID: {current_thread.ident}, Thread Name: {current_thread.name}, Output: {i}")

def main():
    # Create thread objects targeting the print_numbers function
    thread1 = threading.Thread(target=print_numbers, name="MyThread")
    thread2 = threading.Thread(target=print_numbers, name="MySecondThread")

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for both threads to complete execution
    thread1.join()
    thread2.join()

    print("Main program continues after thread execution.")

# if __name__ == "__main__":
#     main()


import multiprocessing

# Function that will run in a separate process
def print_numbers():
    current_process = multiprocessing.current_process()
    for i in range(5):
        print(f"Process ID: {current_process.pid}, Process Name: {current_process.name}, Output: {i}")

def main():
    # Create process objects targeting the print_numbers function
    process1 = multiprocessing.Process(target=print_numbers, name="MyProcess")
    process2 = multiprocessing.Process(target=print_numbers, name="MySecondProcess")

    # Start the processes
    process1.start()
    process2.start()

    # Wait for both processes to complete execution
    process1.join()
    process2.join()

    print("Main program continues after process execution.")

# if __name__ == "__main__":
#     main()
