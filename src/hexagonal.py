
import random
import time
import pmma
import pygame
import math

pmma.init()

canvas = pmma.Display()
canvas.create(1280, 720)
events = pmma.Events(canvas)

UNIFORM = True

registry = pmma.Registry

color_perlin = pmma.Perlin(random.randint(0, 9999))
rotation_perlin = pmma.Perlin(random.randint(0, 9999))

SWITCH = False

def draw_ngon(Surface, color, n, radius, position, rotation=0, width=0, wire_frame=False, cache=None):
    if cache is not None:
        return pygame.draw.polygon(Surface, color, cache, width=width), cache

    pi2 = 2 * math.pi

    if wire_frame:
        for i in range(0, n):
            pygame.draw.line(Surface, color, position, (math.cos(i / n * pi2) * radius + position[0], math.sin(i / n * pi2) * radius + position[1]))

    points = [(math.cos(i / n * pi2 + rotation) * radius + position[0], math.sin(i / n * pi2 + rotation) * radius + position[1]) for i in range(0, n)]
    if wire_frame:
        width = 1

    return pygame.draw.polygon(Surface, color, points, width=width), points

class Hexagon:
    def __init__(self, n, d):
        self.n = n/10
        self.size = n
        self.iter = n
        self.points = None
        self.k = n
        self.d = d

    def render(self, now_time):
        color = [
            color_perlin.generate_2D_perlin_noise((now_time+self.n)/75, 0, [0, 255]),
            color_perlin.generate_2D_perlin_noise(0, (now_time+self.n)/75, [0, 255]),
            color_perlin.generate_2D_perlin_noise(-(now_time+self.n)/75, 0, [0, 255])
        ]
        if clear_cache:
            self.points = None

        _, self.points = draw_ngon(canvas.surface, color, 3, self.size, center, rotation=self.k/(2*math.pi))

        if SWITCH:
          self.k = rotation_perlin.generate_2D_perlin_noise(-(now_time+self.iter)/1000, 0, [0, 360]) # 500
        elif UNIFORM:
            self.k += 0.1
        else:
          self.k += (1-self.d)/2

squares = []
diag = int(math.sqrt(canvas.get_width()**2 + canvas.get_width()**2))
for i in range(0, diag, 4):
    squares.append(Hexagon(diag-i, i/diag))

clear_cache = False

start = time.perf_counter()
now_time = 0
center = (canvas.get_width()/2, canvas.get_height()/2)
while registry.running:
    #k = time.perf_counter()

    canvas.clear(pygame.transform.average_color(canvas.surface))

    event = events.handle()
    for e in event:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_F11:
                clear_cache = True
                center = (canvas.get_width()/2, canvas.get_height()/2)

    for square in squares:
        square.render(now_time)

    clear_cache = False

    canvas.refresh(refresh_rate=60)
    now_time = (time.perf_counter() - start)*5
    #s = time.perf_counter()
