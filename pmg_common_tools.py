import os
import time


FPS = 1.0 / 30


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def print_screen(screen_data):
    clear_screen()
    # TODO: is it possible to make it faster?
    for line in screen_data:
        print(*line, sep="")


def calculate_and_print(func):
    func_start = time.time()
    screen_data = func()
    func_duration = time.time() - func_start
    if func_duration < FPS:
        time.sleep(FPS - func_duration)
    print_screen(screen_data)
