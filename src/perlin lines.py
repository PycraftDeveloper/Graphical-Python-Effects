import pmma
import random
import pygame
import time
import pygame.gfxdraw

display = pmma.Canvas()
events = pmma.Events()
perlin = pmma.Perlin(random.randint(0, 1000000))

display.create_canvas(1280, 720)

start = time.perf_counter()
now = 0
while True:
    display.clear(0, 0, 0)

    for y in range(-100, display.get_height()+100, 10):
        points = []
        for x in range(0, display.get_width()+10, 10):
            points.append((x, y + perlin.generate_2D_perlin_noise(x / 100, (y/100) + (now / 10)) * 50))
        pygame.draw.aalines(display.display, (255, 255, 255), False, points)

    events.handle(display)

    display.refresh(refresh_rate=75)
    now = time.perf_counter()-start