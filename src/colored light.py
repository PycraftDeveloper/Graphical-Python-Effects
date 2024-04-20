import pmma
import random
import time
import pygame

canvas = pmma.Canvas()
canvas.create_canvas(1280, 720)

events = pmma.Events()

registry = pmma.Registry()

now_time = 0
start = time.perf_counter()

class Point:
    def __init__(self):
        self.noise_x = pmma.Perlin(random.randint(0, 999999))
        self.noise_y = pmma.Perlin(random.randint(0, 999999))

        self.noise_s = pmma.Perlin(random.randint(0, 999999))

        self.noise_color = pmma.Perlin(random.randint(0, 999999))

    def compute(self):
        self.x = self.noise_x.generate_2D_perlin_noise(now_time/5, 0, [0, canvas.get_width()])
        self.y = self.noise_y.generate_2D_perlin_noise(now_time/5, 0, [0, canvas.get_height()])

        self.s = self.noise_s.generate_2D_perlin_noise(now_time/100, 0, [1, 10])

        self.r = self.noise_color.generate_2D_perlin_noise(now_time, 0, [0, 255])
        self.g = self.noise_color.generate_2D_perlin_noise(0, now_time, [0, 255])
        self.b = self.noise_color.generate_2D_perlin_noise(now_time, now_time, [0, 255])

    def render(self):
        pygame.draw.circle(canvas.display, (self.r, self.g, self.b), (self.x, self.y), self.s)

points = []
N = 20
for i in range(20):
    points.append(Point())

surface = pygame.Surface((canvas.get_width(), canvas.get_height()))

while registry.running:
    canvas.clear(0, 0, 0)

    events.handle(canvas)

    for point in points:
        point.compute()
        point.render()

    canvas.refresh()
    now_time = time.perf_counter()-start