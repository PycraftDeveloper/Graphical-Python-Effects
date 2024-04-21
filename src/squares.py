
import random
import time
import pmma
import pygame
import math

canvas = pmma.Display()
canvas.create(1280, 720)
events = pmma.Events()

registry = pmma.Registry

color_perlin = pmma.Perlin(random.randint(0, 9999))
rotation_perlin = pmma.Perlin(random.randint(0, 9999))

class Square:
    def __init__(self, n):
        self.surface = pygame.Surface((n, n), pygame.SRCALPHA)
        self.n = n/10

    def render(self, now_time):
        color = [
            color_perlin.generate_2D_perlin_noise((now_time+self.n)/100, 0, [0, 255]),
            color_perlin.generate_2D_perlin_noise(0, (now_time+self.n)/100, [0, 255]),
            color_perlin.generate_2D_perlin_noise(-(now_time+self.n)/100, 0, [0, 255])
        ]
        self.surface.fill(color)

        surface = pygame.transform.rotate(self.surface, self.n)
        canvas.blit(surface, ((canvas.get_width() - surface.get_width())/2, (canvas.get_height() - surface.get_height())/2))

squares = []
diag = int(math.sqrt(canvas.get_width()**2 + canvas.get_height()**2))
for i in range(0, diag, 15):
    squares.append(Square(diag-i))

start = time.perf_counter()
now_time = 0
while registry.running:
    k = time.perf_counter()
    canvas.clear(0, 0, 0)

    events.handle(canvas)

    for square in squares:
        square.render(now_time)
        square.n += 0.1

    canvas.refresh()
    now_time = time.perf_counter() - start
    s = time.perf_counter()
    print(1/(s-k))