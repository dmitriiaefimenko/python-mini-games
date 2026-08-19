from enum import Enum
from os import name as os_name
from subprocess import call
from sys import stdout
from time import time, sleep


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


def paint_char(char, color):
    if color == Color.RED:
        return '\033[91m' + char + '\033[0m'
    if color == Color.GREEN:
        return '\033[92m' + char + '\033[0m'
    if color == Color.BLUE:
        return '\033[94m' + char + '\033[0m'
    return char


def _fps_pause(fps_duration, start_time):
    diff = time() - start_time
    sleep(0 if diff >= fps_duration else fps_duration - diff)


def _clear_screen():
    call('cls' if os_name == 'nt' else 'clear', shell=True)


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
