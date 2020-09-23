from multiprocessing import Process, Pipe, Manager
from os import getpid
from datetime import datetime
from time import sleep

# send time vector to the pipe 
def send(pipe, pid, counter):
    counter[pid] += 1
    pipe.send(counter)

    print(f'{pid} sent a message at time {counter[pid]}.')


# calculate new time vector values given the received vector
def update_counter_on_receive(received_time, counter):
    for pid in range(len(counter)):
        counter[pid] = max(received_time[pid], counter[pid])


# receive time vector from the pipe
def receive(pipe, pid, counter):
    time = pipe.recv()
    update_counter_on_receive(time, counter)

    print(f'{pid} received a message at time {counter[pid]}.')


# simulate a local event
def on_event(pid, counter):
    counter[pid] += 1

    print(f'{pid} had some local event at time {counter[pid]}.')


# procedure for 0'th process (a)
def run_process0(results, pipe01):
    pid = 0
    counter = [0, 0, 0]
    
    send(pipe01, pid, counter)
    send(pipe01, pid, counter)
    on_event(pid, counter)

    # idling
    sleep(1)

    receive(pipe01, pid, counter)
    on_event(pid, counter)
    on_event(pid, counter)
    receive(pipe01, pid, counter)

    results[pid] = counter


# procedure for 1'st process (b)
def run_process1(results, pipe10, pipe12):
    pid = 1
    counter = [0, 0, 0]

    # idling
    sleep(1)

    receive(pipe10, pid, counter)
    receive(pipe10, pid, counter)
    send(pipe10, pid, counter)
    receive(pipe12, pid, counter)
    on_event(pid, counter)
    send(pipe10, pid, counter)
    send(pipe12, pid, counter)
    send(pipe12, pid, counter)

    results[pid] = counter


# procedure for 2'nd process (c)
def run_process2(results, pipe21):
    pid = 2
    counter = [0, 0, 0]

    send(pipe21, pid, counter)

    # idling
    sleep(7)

    receive(pipe21, pid, counter)
    on_event(pid, counter)
    receive(pipe21, pid, counter)

    results[pid] = counter


if __name__ == '__main__':
    pipe01, pipe10 = Pipe()
    pipe12, pipe21 = Pipe()

    manager = Manager()
    results = manager.list([[], [], []])

    process0 = Process(target=run_process0, 
                       args=(results, pipe01,))
    process1 = Process(target=run_process1, 
                       args=(results, pipe10, pipe12))
    process2 = Process(target=run_process2, 
                       args=(results, pipe21,))

    process0.start()
    process1.start()
    process2.start()

    process0.join()
    process1.join()
    process2.join()

    print(f'Process a {results[0]}')
    print(f'Process b {results[1]}')
    print(f'Process c {results[2]}')