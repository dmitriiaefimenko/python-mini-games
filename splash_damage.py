from common import main_loop
from enum import Enum
from keyboard import is_pressed
from random import Random


fps = (20, 1 / 20)
rnd = Random()
flicker_rate = flicker_timer = 8 * fps[0]
enemy_spawn_rate = enemy_spawn_timer = 2 * fps[0]
unit_speed = 3.2 / fps[0]
enemy_speed = 1.8 / fps[0]
projectile_speed = 4.8 / fps[0]


class Char(Enum):
    EMPTY = ' '
    UNIT = '\033[94m◍\033[0m'
    ENEMY = '\033[92m◯\033[0m'
    PROJECTILE_H = '⎯'
    PROJECTILE_V = '|'
    PROJECTILE_HVL = '\\'
    PROJECTILE_HVR = '/'
    EXPLOSION = '\033[91m✷\033[0m'
    BORDER_RED = '\033[91m*\033[0m'
    BORDER_BLUE = '\033[94m*\033[0m'


class Stage(Enum):
    START = 0
    MAIN = 1
    END_WON = 2
    END_LOST = 3


class Unit:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.int_pos_x = int(self.pos_x)
        self.int_pos_y = int(self.pos_y)
        self.speed = unit_speed
        self.reload_rate = fps[0]
        self.reload = 0
        self.defeated = False
        self.left_to_defeat = 20

    def move(self, screen_data):
        global projectiles
        direction_x = 0
        direction_y = 0
        if is_pressed('a') and not is_pressed('d'):
            direction_x = -1
        elif is_pressed('d') and not is_pressed('a'):
            direction_x = 1
        if is_pressed('w') and not is_pressed('s'):
            direction_y = -1
        elif is_pressed('s') and not is_pressed('w'):
            direction_y = 1
        if screen_data[int(self.pos_y + self.speed * direction_y)][int(self.pos_x + self.speed * direction_x)] in {
            Char.EMPTY.value}:
            self.pos_x += self.speed * direction_x
            self.pos_y += self.speed * direction_y
            self.int_pos_x = int(self.pos_x)
            self.int_pos_y = int(self.pos_y)
        screen_data[self.int_pos_y][self.int_pos_x] = Char.UNIT.value
        if self.reload > 0:
            self.reload -= 1
        elif is_pressed('space') and (self.speed * direction_x != 0 or self.speed * direction_y != 0):
            self.reload = self.reload_rate
            projectile_pos_x = self.pos_x
            projectile_pos_y = self.pos_y
            while int(projectile_pos_x) == self.int_pos_x and int(projectile_pos_y) == self.int_pos_y:
                projectile_pos_x += self.speed * direction_x
                projectile_pos_y += self.speed * direction_y
            projectiles.append(Projectile(projectile_pos_x, projectile_pos_y, direction_x, direction_y, True))


class Enemy:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.int_pos_x = int(self.pos_x)
        self.int_pos_y = int(self.pos_y)
        self.old_pos_x = 0
        self.old_pos_y = 0
        self.direction_x = self.direction_y = 0
        self.speed = enemy_speed
        self.reload = rnd.randint(fps[0] // 2, fps[0] * 2)

    def move(self, screen_data):
        global unit
        if self.int_pos_x != self.old_pos_x or self.int_pos_y != self.old_pos_y or self.direction_x == self.direction_y == 0 or screen_data[int(self.pos_y + self.speed * self.direction_y)][int(self.pos_x + self.speed * self.direction_x)] != Char.EMPTY.value:
            self.direction_x = rnd.randint(-1, 1)
            self.direction_y = rnd.randint(-1, 1)
            self.old_pos_x = self.int_pos_x
            self.old_pos_y = self.int_pos_y
        if screen_data[int(self.pos_y + self.speed * self.direction_y)][int(self.pos_x + self.speed * self.direction_x)] == Char.EMPTY.value:
            self.pos_x += self.speed * self.direction_x
            self.pos_y += self.speed * self.direction_y
            self.int_pos_x = int(self.pos_x)
            self.int_pos_y = int(self.pos_y)
        if self.reload > 0:
            self.reload -= 1
        else:
            self.reload = rnd.randint(fps[0] // 2, fps[0] * 2)
            direction_x = 1 if unit.int_pos_x > self.int_pos_x else -1
            direction_y = 1 if unit.int_pos_y > self.int_pos_y else -1
            if abs(unit.int_pos_x - self.int_pos_x) > abs(unit.int_pos_y - self.int_pos_y):
                direction_y = 0
            else:
                direction_x = 0
            projectile_pos_x = self.pos_x
            projectile_pos_y = self.pos_y
            while int(projectile_pos_x) == self.int_pos_x and int(projectile_pos_y) == self.int_pos_y:
                projectile_pos_x += self.speed * direction_x
                projectile_pos_y += self.speed * direction_y
            projectiles.append(Projectile(projectile_pos_x, projectile_pos_y, direction_x, direction_y, False))
        screen_data[self.int_pos_y][self.int_pos_x] = Char.ENEMY.value


class Projectile:
    def __init__(self, pos_x, pos_y, direction_x, direction_y, is_unit):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.int_pos_x = int(self.pos_x)
        self.int_pos_y = int(self.pos_y)
        self.speed_x = projectile_speed * direction_x
        self.speed_y = projectile_speed * direction_y
        if direction_x == direction_y == 1 or direction_x == direction_y == -1:
            self.char = Char.PROJECTILE_HVL
        elif direction_x > 0 > direction_y or direction_x < 0 < direction_y:
            self.char = Char.PROJECTILE_HVR
        elif direction_x == 0:
            self.char = Char.PROJECTILE_V
        else:
            self.char = Char.PROJECTILE_H
        self.is_unit = is_unit

    def move(self, screen_data):
        global projectiles, unit, enemies
        new_pos_x = self.pos_x + self.speed_x
        new_pos_y = self.pos_y + self.speed_y
        int_pos_x = int(new_pos_x)
        int_pos_y = int(new_pos_y)
        for enemy in enemies:
            if int_pos_x == enemy.int_pos_x and int_pos_y == enemy.int_pos_y:
                explosions.append(Explosion(self.int_pos_x, self.int_pos_y, self.is_unit))
                projectiles.remove(self)
                return
        if screen_data[int_pos_y][int_pos_x] == Char.EMPTY.value and (int_pos_x != unit.int_pos_x or int_pos_y != unit.int_pos_y):
            self.pos_x = new_pos_x
            self.pos_y = new_pos_y
            self.int_pos_x = int_pos_x
            self.int_pos_y = int_pos_y
            screen_data[self.int_pos_y][self.int_pos_x] = self.char.value
        else:
            explosions.append(Explosion(self.int_pos_x, self.int_pos_y, self.is_unit))
            projectiles.remove(self)


class Explosion:
    def __init__(self, pos_x, pos_y, is_unit):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_unit = is_unit
        self.stage = 0
        self.frames_per_stage = fps[0] // 6
        self.timer = self.frames_per_stage

    def move(self, screen_data):
        global explosions
        if self.stage == 0:
            self._stage_0(screen_data)
        elif self.stage == 1:
            self._stage_1(screen_data)
        elif self.stage == 2:
            self._stage_2(screen_data)
        elif self.stage == 3:
            self._stage_3(screen_data)
        else:
            explosions.remove(self)
            return
        if self.timer > 0:
            self.timer -= 1
        else:
            self.stage += 1
            self.timer = self.frames_per_stage

    def _process_position(self, screen_data, pos_x, pos_y):
        global unit, enemies, projectiles, explosions
        if pos_x >= len(screen_data[0]) or pos_x < 0 or pos_y >= len(screen_data) or pos_y < 0 or screen_data[pos_y][pos_x] == Char.EXPLOSION.value:
            return
        for projectile in projectiles:
            if projectile.int_pos_x == pos_x and projectile.int_pos_y == pos_y:
                explosions.append(Explosion(pos_x, pos_y, self.is_unit))
                projectiles.remove(projectile)
                return
        for enemy in enemies:
            if enemy.int_pos_x == pos_x and enemy.int_pos_y == pos_y:
                if self.is_unit:
                    unit.left_to_defeat = 0 if unit.left_to_defeat == 0 else unit.left_to_defeat - 1
                explosions.append(Explosion(pos_x, pos_y, self.is_unit))
                enemies.remove(enemy)
                return
        if unit.int_pos_x == pos_x and unit.int_pos_y == pos_y:
            unit.defeated = True
            return
        if screen_data[pos_y][pos_x] == Char.EMPTY.value:
            screen_data[pos_y][pos_x] = Char.EXPLOSION.value

    def _stage_0(self, screen_data):
        # - - - - -
        # - - - - -
        # - - * - -
        # - - - - -
        # - - - - -
        self._process_position(screen_data, self.pos_x, self.pos_y)

    def _stage_1(self, screen_data):
        # - - - - -
        # - - * - -
        # - * - * -
        # - - * - -
        # - - - - -
        self._stage_0(screen_data)
        self._process_position(screen_data, self.pos_x - 1, self.pos_y)
        self._process_position(screen_data, self.pos_x, self.pos_y - 1)
        self._process_position(screen_data, self.pos_x + 1, self.pos_y)
        self._process_position(screen_data, self.pos_x, self.pos_y + 1)

    def _stage_2(self, screen_data):
        # - - * - -
        # - * - * -
        # * - - - *
        # - * - * -
        # - - * - -
        self._stage_1(screen_data)
        self._process_position(screen_data, self.pos_x - 2, self.pos_y)
        self._process_position(screen_data, self.pos_x - 1, self.pos_y - 1)
        self._process_position(screen_data, self.pos_x, self.pos_y - 2)
        self._process_position(screen_data, self.pos_x + 1, self.pos_y - 1)
        self._process_position(screen_data, self.pos_x + 2, self.pos_y)
        self._process_position(screen_data, self.pos_x + 1, self.pos_y + 1)
        self._process_position(screen_data, self.pos_x, self.pos_y + 2)
        self._process_position(screen_data, self.pos_x - 1, self.pos_y + 1)

    def _stage_3(self, screen_data):
        # - * - * -
        # * - - - *
        # - - - - -
        # * - - - *
        # - * - * -
        self._stage_2(screen_data)
        self._process_position(screen_data, self.pos_x - 2, self.pos_y - 1)
        self._process_position(screen_data, self.pos_x - 1, self.pos_y - 2)
        self._process_position(screen_data, self.pos_x + 1, self.pos_y - 2)
        self._process_position(screen_data, self.pos_x + 2, self.pos_y - 1)
        self._process_position(screen_data, self.pos_x + 2, self.pos_y + 1)
        self._process_position(screen_data, self.pos_x + 1, self.pos_y + 2)
        self._process_position(screen_data, self.pos_x - 1, self.pos_y + 2)
        self._process_position(screen_data, self.pos_x - 2, self.pos_y + 1)


stage = Stage.START
unit: Unit
enemies = list()
projectiles = list()
explosions = list()

start_screen = \
'''
01010101010101010101010101010101
1                              0
0                              1
1                              0
0                              1
1                              0
0                              1
1                              0
0                              1
1                              0
0                              1
1      10101010101010101       0
0      0               0       1
1      1 SPLASH DAMAGE 1       0
0      0               0       1
1      10101010101010101       0
0                              1
1                              0
0                              1
1                              0
0                              1
1    CONTROLS:                 0
0    W, S, A, D - MOVE         1
1    SPACE      - SHOOT        0
0    ENTER      - START        1
1                              0
0                              1
1                              0
0                              1
1                              0
0                              1
1                              0
01010101010101010101010101010101
'''

main_screen = \
'''
╔══════════════════════════════╗
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
║                              ║
╚══════════════════════════════╝
'''

end_screen_won = \
'''
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
0101010101            0101010101
1010101010  VICTORY!  1010101010
0101010101            0101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010                      10101
10101   ENTER - TRY AGAIN  01010
01010   ESC   - EXIT       10101
10101                      01010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
10101010101010101010101010101010
01010101010101010101010101010101
'''

end_screen_lost = \
'''
01010101010101010101010101010101
1                              1
0                              0
1                              1
0                              0
1                              1
0                              0
1     1111111111111111111      1
0     1000000000000000001      0
1     1011111111111111101      1
0     101             101      0
1     101  DEFEATED!  101      1
0     101             101      0
1     1011111111111111101      1
0     1000000000000000001      0
1     1111111111111111111      1
0                              0
1 1010101010101010101010101010 1
0 0101010101010101010101010101 0
1 1010101010101010101010101010 1
0 010                      101 0
1 101   ENTER - TRY AGAIN  010 1
0 010   ESC   - EXIT       101 0
1 101                      010 1
0 0101010101010101010101010101 0
1 1010101010101010101010101010 1
0 0101010101010101010101010100 0
1                              1
0                              0
1                              1
0                              0
1                              1
01010101010101010101010101010101
'''


def _convert_template(template):
    return [list(line) for line in template.strip('\n').split('\n')]


def _get_random_position(screen_data):
    for i in range(5):
        pos_x = rnd.randint(1, len(screen_data[0]) - 2)
        pos_y = rnd.randint(1, len(screen_data) - 2)
        if screen_data[pos_y][pos_x] == Char.EMPTY.value:
            return True, pos_x, pos_y
    return False, 0, 0


def _add_description(screen_data):
    global unit
    reload_indicator = int(unit.reload * 100 / unit.reload_rate)
    screen_data.append(list('RELOAD:[' + '#' * (reload_indicator // 10) + ' ' * (10 - reload_indicator // 10) + '] LEFT:' + str(unit.left_to_defeat)))


def _spawn_enemy(screen_data):
    global enemy_spawn_rate, enemy_spawn_timer
    if enemy_spawn_timer > 0:
        enemy_spawn_timer -= 1
        return
    found, pos_x, pos_y = _get_random_position(screen_data)
    if found:
        enemies.append(Enemy(pos_x, pos_y))
        enemy_spawn_rate = fps[0] // 2 if enemy_spawn_rate - 1 < fps[0] // 2 else enemy_spawn_rate - 1
        enemy_spawn_timer = enemy_spawn_rate


def _get_border_char(char):
    global flicker_rate, flicker_timer
    flicker_timer = flicker_timer - 1 if flicker_timer - 1 > 0 else flicker_rate
    if flicker_timer > flicker_rate // 2:
        if char == '0':
            return Char.BORDER_RED.value
        else:
            return Char.BORDER_BLUE.value

    else:
        if char == '0':
            return Char.BORDER_BLUE.value
        else:
            return Char.BORDER_RED.value


def _calculate_start_stage():
    global stage
    if is_pressed('enter'):
        stage = Stage.MAIN
    screen_data = _convert_template(start_screen)
    for line in screen_data:
        for i in range(len(line)):
            if line[i] in ('0', '1'):
                line[i] = _get_border_char(line[i])
    return screen_data


def _calculate_main_stage():
    global stage, unit, enemies, projectiles
    screen_data = _convert_template(main_screen)
    for projectile in projectiles:
        projectile.move(screen_data)
    for explosion in explosions:
        explosion.move(screen_data)
    for enemy in enemies:
        enemy.move(screen_data)
    unit.move(screen_data)
    _add_description(screen_data)
    _spawn_enemy(screen_data)
    if unit.defeated:
        stage = Stage.END_LOST
    elif unit.left_to_defeat == 0:
        stage = Stage.END_WON
    return screen_data


def _calculate_end_stage():
    global stage
    screen_data = _convert_template(end_screen_won if stage == Stage.END_WON else end_screen_lost)
    for line in screen_data:
        for i in range(len(line)):
            if line[i] in ('0', '1'):
                line[i] = _get_border_char(line[i])
    done = False
    if is_pressed('enter'):
        init_func()
        stage = stage.MAIN
    elif is_pressed('escape'):
        done = True
    return screen_data, done


def init_func():
    global unit, enemies, projectiles, explosions, enemy_spawn_rate, enemy_spawn_timer
    enemies = list()
    projectiles = list()
    explosions = list()
    enemy_spawn_rate = enemy_spawn_timer = 2 * fps[0]
    screen_data = _convert_template(main_screen)
    while True:
        found, pos_x, pos_y = _get_random_position(screen_data)
        if found:
            break
    unit = Unit(pos_x, pos_y)
    screen_data[pos_x][pos_y] = Char.UNIT.value
    for i in range(3):
        found, pos_x, pos_y = _get_random_position(screen_data)
        if found:
            enemies.append(Enemy(pos_x, pos_y))
            screen_data[pos_y][pos_x] = Char.ENEMY.value


def calculate_data_func():
    global stage
    if stage == Stage.START:
        return _calculate_start_stage(), False
    if stage == Stage.MAIN:
        return _calculate_main_stage(), False
    return _calculate_end_stage()


main_loop(init_func, calculate_data_func, fps[1])
