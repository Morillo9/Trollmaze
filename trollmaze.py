#! /usr/bin/python

import pygame
import random
from pygame import *
from spritesheet import *

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

wall_sprite = wall_resource.image_at((0, 0, 32, 32), colorkey=(-1))
floor_srite = floor_resource.image_at((0, 0, 32, 32), colorkey=(-1))
exit_sprite = exit_resource.image_at((0, 0, 32, 32), colorkey=(-1))
player_left = player_resource.image_at((0, 0, 16, 16), colorkey=(-1))
player_right = player_resource.image_at((32, 0, 16, 16), colorkey=(-1))
player_up = player_resource.image_at((0, 16, 16, 16), colorkey=(-1))
player_down = player_resource.image_at((32, 32, 16, 16), colorkey=(-1))


def main():
    global cameraX, cameraY
    timer = pygame.time.Clock()

    up = down = left = right = running = False
    bg = Surface((32,32))
    bg.convert()
    bg.fill(Color("#181818"))
    entities = pygame.sprite.Group()
    player = Player(16, 16)
    platforms = []
    x, y = 0, 0

    level = [
           '#####################################',
           '# #       #       #     #         # #',
           '# # ##### # ### ##### ### ### ### # #',
           '#       #   # #     #     # # #   # #',
           '##### # ##### ##### ### # # # ##### #',
           '#   # #       #     # # # # #     # #',
           '# # ####### # # ##### ### # ##### # #',
           '# #       # # #   #     #     #   # #',
           '# ####### ### ### # ### ##### # ### #',
           '#     #   # #   # #   #     # #     #',
           '# ### ### # ### # ##### # # # #######',
           '#   #   # # #   #   #   # # #   #   #',
           '####### # # # ##### # ### # ### ### #',
           '#     # #     #   # #   # #   #     #',
           '# ### # ##### ### # ### ### ####### #',
           '# #   #     #     #   # # #       # #',
           '# # ##### # ### ##### # # ####### # #',
           '# #     # # # # #     #       # #   #',
           '# ##### # # # ### ##### ##### # #####',
           '# #   # # #     #     # #   #       #',
           '# # ### ### ### ##### ### # ##### # #',
           '# #         #     #       #       # #',
           '#X###################################',]


    while True:
        rand_x = random.randint(1, len(level) -1)
        rand_y = random.randint(1, len(level[0]) -1)

        if level[rand_x][rand_y] == " ":
            player.rect.y = rand_x * 32 + 8
            player.rect.x = rand_y * 32 + 8
            break

    # build the level
    for row in level:
        for col in row:
            if col == "#":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "X":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)


            x += 32
        y += 32
        x = 0

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

        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        camera.update(player)

        # update player, draw everything else
        player.update(up, down, left, right, running, platforms)
        for e in entities:
            screen.blit(e.image, camera.apply(e))

        pygame.display.update()

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
        self.onGround = False
        self.image = player_left
        self.image.convert()
        self.rect = Rect(x, y, 16, 16)

    def update(self, up, down, left, right, running, platforms):
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
        # assuming we're in the air
        self.onGround = False;
        # do y-axis collisions
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    pygame.event.post(pygame.event.Event(QUIT))
                if xvel > 0:
                    self.rect.right = p.rect.left
                    print ("collide right")
                if xvel < 0:
                    self.rect.left = p.rect.right
                    print ("collide left")
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom


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

if __name__ == "__main__":
    main()
