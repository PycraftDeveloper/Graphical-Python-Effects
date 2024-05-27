import pmma

import pygame

import time

import random

import math as M

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

DETAIL = 200
NUMBER_OF_LINES = 500
seed = pmma.Perlin()
RANGE = [-1000, 1000]

class Line:
    def __init__(self, k):
        self.centre = display.get_width() / 2, display.get_height() / 2
        self.direction = (random.random()*2)-1, (random.random()*2)-1
        self.k = k

    def compute(self, time):
        self.centre = display.get_width() / 2, display.get_height() / 2
        points = []
        x, y = self.centre
        for r in range(DETAIL):
            points.append((x, y))
            x += seed.generate_2D_perlin_noise(M.sin(r)/100, M.cos(self.k+now_time)/100, range=RANGE)
            y += seed.generate_2D_perlin_noise(M.cos(r)/100, M.sin(self.k+now_time)/100, range=RANGE)

        return points

    def render(self, surface, color, time):
        points = self.compute(time)
        pygame.draw.lines(surface, color, False, points, width=1)

lines = []
for k in range(NUMBER_OF_LINES):
    lines.append(Line(k))

surface = pygame.Surface(display.get_size())
surface.fill((0, 0, 0))
for line in lines:
    line.render(surface, (255, 255, 255), now_time)
surface.set_colorkey([255, 255, 255])
refresh = False
while True:
    display.clear()

    center = display.get_width() / 2, display.get_height() / 2

    for r in range(number_of_circles, 0, -10):
        ar = (now_time + r) / 500
        color = [
            background_perlin.generate_2D_perlin_noise(ar, 0, range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(0, ar, range=[0, 255]),
            background_perlin.generate_2D_perlin_noise(-ar, 0, range=[0, 255])]
        draw.circle(color, center, r)

    if refresh:
        surface = pygame.Surface(display.get_size())
        surface.fill((0, 0, 0))
        for line in lines:
            line.render(surface, (255, 255, 255), now_time)
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