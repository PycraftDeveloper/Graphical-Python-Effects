import pmma
import random
import time
import pygame

#pmma.init()

display = pmma.Display()
display.create(1280, 720)

events = pmma.Events(display)

draw = pmma.Draw(display)

now_time = 0
start = time.perf_counter()

class Point:
    def __init__(self):
        self.noise_x = pmma.Perlin()
        self.noise_y = pmma.Perlin()

        self.noise_s = pmma.Perlin()

        self.noise_color = pmma.Perlin()

    def compute(self):
        self.x = self.noise_x.generate_2D_perlin_noise(now_time/5, 0, [0, display.get_width()])
        self.y = self.noise_y.generate_2D_perlin_noise(now_time/5, 0, [0, display.get_height()])

        self.s = self.noise_s.generate_2D_perlin_noise(now_time/100, 0, [1, 10])

        self.r = self.noise_color.generate_2D_perlin_noise(now_time, 0, [0, 255])
        self.g = self.noise_color.generate_2D_perlin_noise(0, now_time, [0, 255])
        self.b = self.noise_color.generate_2D_perlin_noise(now_time, now_time, [0, 255])

    def render(self):
        draw.circle((self.r, self.g, self.b), (self.x, self.y), self.s)

points = []
N = 20
for i in range(N):
    points.append(Point())

surface = pygame.Surface((display.get_width(), display.get_height()))

while pmma.Registry.running:
    display.clear(0, 0, 0)

    events.handle()

    for point in points:
        point.compute()
        point.render()

    display.refresh()
    now_time = time.perf_counter()-start