import math
import time
import random

import pygame
import pygame.gfxdraw

pygame.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN, vsync=1)
display.convert()

clock = pygame.time.Clock()

start = time.perf_counter()
now_time = 0

window_x, window_y = display.get_size()
dsc = ((window_x**2) + (window_y**2))**0.5
o = int((dsc*math.cos(1/4 * math.pi)))

mask = pygame.Surface((window_x, window_y))
mask.fill([0, 0, 0])
c = window_x/2, window_y/2
pygame.draw.circle(mask, (255, 0, 0), c, window_y/2)
mask.set_colorkey([255, 0, 0])
mask = mask.convert_alpha()

x = window_x/2
y = window_y/2

r = random.randint(100, 255)
g = random.randint(100, 255)
b = random.randint(100, 255)

dr = 1
dg = -1
db = 1
while True:
    window_x, window_y = display.get_size()

    for i in range(300):
        x_option = random.randint(0, 2)
        y_option = random.randint(0, 2)

        if x_option == 0:
            x += 1
        elif x_option == 1:
            x -= 1
        if y_option == 0:
            y += 1
        elif y_option == 1:
            y -= 1

        if x < 0:
            x = 0
        elif x > window_x-1:
            x = window_x-1

        if y < 0:
            y = 0
        elif y > window_y-1:
            y = window_y-1

        pygame.gfxdraw.pixel(display, int(x), int(y), (r, g, b))

    r += random.random()*dr
    g += random.random()*dg
    b += random.random()*db

    if r > 255:
        r = 255
        dr = -1
    elif r < 100:
        r = 100
        dr = 1

    if g > 255:
        g = 255
        dg = -1
    elif g < 100:
        g = 100
        dg = 1

    if b > 255:
        b = 255
        db = -1
    elif b < 100:
        b = 100
        db = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

            if event.key == pygame.K_SPACE:
                display.fill([0, 0, 0])

    pygame.display.flip()
    #clock.tick(500)
    now_time = time.perf_counter()-start