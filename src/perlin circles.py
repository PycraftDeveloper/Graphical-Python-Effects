import pmma
import random
import pygame
import time
import pygame.gfxdraw
import math

display = pmma.Canvas()
events = pmma.Events()
perlin = pmma.Perlin(random.randint(0, 1000000))

def conv(deg):
    return math.radians(deg)

display.create_canvas(1280, 720)

start = time.perf_counter()
now = 0
while True:
    display.clear(0, 0, 0)

    size = (1+math.sin(now))

    for n in range(0, display.get_height(), 20):
        points = []
        for x in range(0, 361, 3):
            points.append([
                (display.get_width()-math.sin(conv(x))*(n*size*perlin.generate_2D_perlin_noise(now, n)))/2,
                (display.get_height()-math.cos(conv(x))*(n*size*perlin.generate_2D_perlin_noise(now, -n)))/2])
        pygame.draw.aalines(display.display, (255, 255, 255), False, points)

    events.handle(display)

    display.refresh(refresh_rate=75)
    now = time.perf_counter()-start