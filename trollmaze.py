#! /usr/bin/python

import pygame
import random
from pygame import *
from spritesheet import *
from mazegenerator import *


WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

pygame.init()
screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
pygame.display.set_caption("Use arrows to move!")

floor_resource = Spritesheet('./Floor.png')
wall_resource = Spritesheet('./Wall.png')
player_resource = Spritesheet('./hero.png')
exit_resource = Spritesheet('./Exit.png')
troll_resource = Spritesheet('./troll_1.png')

wall_sprite = wall_resource.image_at((0, 0, 32, 32), colorkey=(-1))
floor_srite = floor_resource.image_at((0, 0, 32, 32), colorkey=(-1))
exit_sprite = exit_resource.image_at((0, 0, 32, 32), colorkey=(-1))
troll_sprite = troll_resource.image_at((0, 0, 20, 25), colorkey=(-1))
player_left = player_resource.image_at((0, 0, 16, 16), colorkey=(-1))
player_right = player_resource.image_at((32, 0, 16, 16), colorkey=(-1))
player_up = player_resource.image_at((0, 16, 16, 16), colorkey=(-1))
player_down = player_resource.image_at((32, 32, 16, 16), colorkey=(-1))


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)

class Entity(pygame.sprite.Sprite):


    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):

    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.image = player_left
        self.image.convert()
        self.rect = Rect(x, y, 16, 16)
        self.move_blocks = False

    def update(self, up, down, left, right, platforms):
        if up:
            self.yvel = -1
        if down:
            self.yvel = 1
        if left:
            self.xvel = -1
        if right:
            self.xvel = 1

        if not(left or right):
            self.xvel = 0

        if not(up or down):
            self.yvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms)
        # increment in y direction
        self.rect.top += self.yvel
        # do y-axis collisions
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    pygame.event.post(pygame.event.Event(QUIT))
                if xvel > 0:
                    self.rect.right = p.rect.left
                if xvel < 0:
                    self.rect.left = p.rect.right
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom

                if self.move_blocks is True:
                    x = p.rect.x
                    y = p.rect.y

                    if self.image == player_up and (x, y - 32) not in platform_dict:
                        p.rect.y -= 32
                        platform_dict.append((x, y - 32))
                        platform_dict.remove((x, y))
                    elif self.image == player_right and (x + 32, y) not in platform_dict:
                        p.rect.x += 32
                        platform_dict.append((x + 32, y))
                        platform_dict.remove((x, y))
                    elif self.image == player_down and (x, y + 32) not in platform_dict:
                        p.rect.y += 32
                        platform_dict.append((x, y + 32))
                        platform_dict.remove((x, y))
                    elif self.image == player_left and (x - 32, y) not in platform_dict:
                        p.rect.x -= 32
                        platform_dict.append((x - 32,  y))
                        platform_dict.remove((x, y))

                    self.move_blocks = False

class Troll(Entity):

    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = random.choice([-1, 1, 0])
        self.yvel = 0 if self.xvel != 0 else random.choice([-1, 1])
        self.image = troll_sprite
        self.image.convert()
        self.rect = Rect(x, y, 20, 25)

    def update(self, platforms):
        self.rect.left += self.xvel
        self.collide(self.xvel, 0, platforms)
        self.rect.top += self.yvel
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                if xvel < 0:
                    self.rect.left = p.rect.right
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom

                if self.xvel == 0:
                    self.yvel = 0
                    self.xvel = random.choice([-1, 1])
                elif self.yvel == 0:
                    self.xvel = 0
                    self.yvel = random.choice([-1, 1])


class Platform(Entity):

    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = wall_sprite
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class Floor(Entity):

    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = floor_srite
        self.rect = Rect(x, y, 32, 32)


class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = exit_sprite
        self.rect = Rect(x, y, 32, 32)


def main():
    global cameraX, cameraY, entities, platforms, bg, platform_dict
    timer = pygame.time.Clock()

    up = down = left = right = running = False
    bg = Surface((32,32))
    bg.convert()
    bg.fill(Color("#181818"))
    player = Player(16, 16)
    platforms, platform_dict, troll_dictionary = [], [], []
    entities = pygame.sprite.Group()
    x, y = 0, 0
    level = create_maze()

    while True:
        rand_x = random.randint(1, len(level[0])-1)
        rand_y = random.randint(1, len(level)-1)

        if level[rand_y][rand_x] == " ":
            player.rect.x = rand_x * 32 + 8
            player.rect.y = rand_y * 32 + 8
            break


    while len(troll_dictionary) < 10:

        rand_x = random.randint(1, len(level[0])-1)
        rand_y = random.randint(1, len(level)-1)
        tmp_troll = Troll(20, 25)

        if level[rand_y][rand_x] == " ":
            tmp_troll.rect.x = rand_x * 32 + 8
            tmp_troll.rect.y = rand_y * 32 + 8

            troll_dictionary.append(tmp_troll)
            entities.add(tmp_troll)


    # build the level
    for row in level:
        for col in row:
            if col == "#":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
                platform_dict.append((x, y))

            x += 32
        y += 32
        x = 0

    while True:

        a = random.randint(1, len(level[0]) -1)
        b = random.choice([1, len(level) -1])

        if level[b][a] == ' ':
            e= ExitBlock(a * 32, b * 32)
            platforms.append(e)
            entities.add(e)
            break

    total_level_width  = len(level[0])*32
    total_level_height = len(level)*32
    camera = Camera(complex_camera, total_level_width, total_level_height)
    entities.add(player)

    while 1:
        timer.tick(60)

        for e in pygame.event.get():
            if e.type == QUIT: raise SystemExit
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
                player.image = player_up
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True
                player.image = player_down
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
                player.image = player_left
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
                player.image = player_right
            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_DOWN:
                down = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYDOWN and e.key == K_SPACE:
                player.move_blocks = True

        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        camera.update(player)

        # update player, draw everything else
        player.update(up, down, left, right, platforms)
        for troll in troll_dictionary:
            troll.update(platforms)

            if pygame.sprite.collide_circle(troll, player):
                raise SystemExit
        for e in entities:
            screen.blit(e.image, camera.apply(e))

        pygame.display.update()


if __name__ == "__main__":
    main()
