import pmma

import pygame

import time

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
    for line in range(NUMBER_OF_LINES):
        seed = LINE_SEEDS[line]
        x = display.get_width() / 2
        y = display.get_height() / 2
        points = []
        for i in range(100):
            points.append([x, y])
            x += seed.generate_1D_perlin_noise((i + now_time/10)/100, range=[-10, 10])
            y += seed.generate_1D_perlin_noise(-(i + now_time/10)/100, range=[-10, 10])
        pygame.draw.lines(surface, (255, 255, 255), False, points, width=4)

while True:
    surface = pygame.Surface(display.get_size())
    display.clear()

    center = display.get_width() / 2, display.get_height() / 2

    for r in range(number_of_circles, 0, -10):
        ar = (now_time + r) / 500
        color = [
            background_perlin.generate_2D_perlin_noise(ar, 0, range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(0, ar, range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(-ar, 0, range=[0, 255])]
        draw.circle(color, center, r)

    events.handle()

    surface.fill((0, 0, 0))
    line_function()
    surface.set_colorkey([255, 255, 255])
    display.blit(surface, (0, 0))

    display.refresh()
    now_time = -(time.perf_counter() - start)*100