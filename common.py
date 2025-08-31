from os import system, name as os_name
from sys import stdout
from time import time, sleep


def _fps_pause(fps_duration, start_time):
    diff = time() - start_time
    sleep(0 if diff >= fps_duration else fps_duration - diff)


def _clear_screen():
    system('cls' if os_name == 'nt' else 'clear')


def _print_frame(data):
    frame = '\n'.join([' '.join(line) for line in data])
    stdout.write(frame)


def main_loop(init_func, calculate_data_func, fps_duration):
    init_func()
    while True:
        start_time = time()
        data, done = calculate_data_func()
        _clear_screen()
        _print_frame(data)
        _fps_pause(fps_duration, start_time)
        if done:
            break
