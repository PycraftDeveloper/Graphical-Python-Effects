import pmma

import pygame

import time
import threading

display = pmma.Display()
display.create(1280, 720)

events = pmma.Events(canvas=display)

background_perlin = pmma.Perlin()

math = pmma.Math()

draw = pmma.Draw(canvas=display)

start = time.perf_counter()
now_time = 0
number_of_circles = int(math.pythag(*display.get_size()))

surface = pygame.Surface(display.get_size())
rect = pygame.Rect(500, 300, 200, 200)

NUMBER_OF_LINES = 5
LINE_SEEDS = []
for _ in range(NUMBER_OF_LINES):
    LINE_SEEDS.append(pmma.Perlin())

def line_function():
    t = now_time/10
    for line in range(NUMBER_OF_LINES):
        seed = LINE_SEEDS[line]
        x, y = center
        points = []
        for i in range(25):
            points.append([x, y])
            x += seed.generate_2D_perlin_noise((i + t)/100, 0, range=[-20, 20])
            y += seed.generate_2D_perlin_noise(-(i + t)/100, 0, range=[-20, 20])
        pygame.draw.lines(surface, (255, 255, 255), False, points, width=1)

while True:
    display.clear()

    center = display.get_width() / 2, display.get_height() / 2

    for r in range(number_of_circles, 0, -25):
        ar = (now_time + r) / 500
        color = [
            background_perlin.generate_2D_perlin_noise(ar, 0, range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(0, ar, range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(-ar, 0, range=[0, 255])]
        draw.circle(color, center, r)

    event_arr = events.handle()

    surface = pygame.Surface(display.get_size())
    surface.fill((0, 0, 0))
    line_function()
    surface.set_colorkey([255, 255, 255])

    display.blit(surface, (0, 0))

    display.refresh()
    now_time = -(time.perf_counter() - start)*100