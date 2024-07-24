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
number_of_circles = int(math.pythag(display.get_size()))

surface = pygame.Surface(display.get_size())
rect = pygame.Rect(500, 300, 200, 200)

NUMBER_OF_LINES = 200
LINE_SEEDS = []
for _ in range(NUMBER_OF_LINES):
    LINE_SEEDS.append(pmma.Perlin())

def line_function():
    k = 0
    for line in range(NUMBER_OF_LINES):
        print(f"Generating {k} of {NUMBER_OF_LINES}")
        seed = LINE_SEEDS[line]
        x = display.get_width() / 2
        y = display.get_height() / 2
        points = []
        for i in range(100):
            points.append([x, y])
            x += seed.generate_2D_perlin_noise((i + now_time/10)/100, 0, new_range=[-10, 10])
            y += seed.generate_2D_perlin_noise(-(i + now_time/10)/100, 0, new_range=[-10, 10])
        pygame.draw.lines(surface, (255, 255, 255), False, points, width=1)
        k += 1

surface = pygame.Surface(display.get_size())
surface.fill((0, 0, 0))
line_function()
surface.set_colorkey([255, 255, 255])
refresh = False
while True:
    display.clear()

    center = display.get_width() / 2, display.get_height() / 2

    for r in range(number_of_circles, 0, -10):
        ar = (now_time + r) / 500
        color = [
            background_perlin.generate_2D_perlin_noise(ar, 0, new_range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(0, ar, new_range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(-ar, 0, new_range=[0, 255])]
        draw.circle(color, center, r)

    if refresh:
        surface = pygame.Surface(display.get_size())
        surface.fill((0, 0, 0))
        line_function()
        surface.set_colorkey([255, 255, 255])
        refresh = False

    event_arr = events.handle()
    for event in event_arr:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                refresh = True

    display.blit(surface, (0, 0))

    display.refresh()
    now_time = -(time.perf_counter() - start)*100