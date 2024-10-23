import pmma
import random
import time
import math
import pygame

pmma.init(log_information=True)

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

events = pmma.Events()

registry = pmma.Registry

color = pmma.Color()

radius = pmma.Math().pythag(display.get_size())/4.2

PETALS = 8

clock = pygame.time.Clock()

class Point:
    def __init__(self):
        self.x = random.randint(0, display.get_width())
        self.y = random.randint(0, display.get_height())

    def compute(self):
        self.x = int(display.get_width()/2 + (radius * math.sin(PETALS * now_time/10)) * math.cos(now_time/10 + 0))
        self.y = int(display.get_height()/2 + (radius * math.sin(PETALS * now_time/10)) * math.sin(now_time/10 + 0))

    def render(self, color):
        self.compute()

        pygame.draw.circle(Surface, color, (self.x, self.y), 10)

point = Point()

start = time.perf_counter()
now_time = 0
i = 0
while registry.running:
    window_x, window_y = display.get_size()
    window_size = (window_x, window_y)

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))

    color_value = color.generate_color_from_perlin_noise(now_time/10, format=pmma.Constants.RGB, color_range=[100, 255])

    #display.clear()

    events.handle()

    point.render(color_value)

    Surface2.set_alpha(1) # 10

    if i % 8 == 0:
        display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    pmma.compute()

    pygame.display.flip()

    clock.tick(60)

    now_time = time.perf_counter() - start

    i += 1

pmma.quit()