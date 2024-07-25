import pmma
import time
import pygame
import random

display = pmma.Display()
display.create(1920, 1080, fullscreen=True)

draw = pmma.Draw()

events = pmma.Events()

scale = 100

class Wave:
    def __init__(self):
        self.color = [pmma.Perlin(),pmma.Perlin(), pmma.Perlin()]
        self.heights = pmma.Perlin()
        self.speed = random.randint(1, 5)

        self.points = []

    def render(self):
        color = [
                self.color[0].generate_1D_perlin_noise((now_time)/25, new_range=[0, 255]),
                self.color[1].generate_1D_perlin_noise((now_time)/25, new_range=[0, 255]),
                self.color[2].generate_1D_perlin_noise((now_time)/25, new_range=[0, 255])]

        points = [(0, display.get_height())]
        height = self.heights.generate_1D_perlin_noise((-now_time/5), new_range=[0, display.get_height()])
        self.points.append(height)
        if len(self.points) > display.get_width():
            del self.points[0]

        x = 0
        for point in self.points:
            points.append((x, point))
            x += 1

        points.append((display.get_width(), display.get_height()))

        pygame.draw.polygon(display.surface, color, points)

now_time = 0
N = 5
waves = []
for i in range(N):
    w = Wave()
    waves.append(w)

start = time.perf_counter()
while pmma.Registry.running:
    display.clear(pygame.transform.average_color(display.surface))

    events.handle()

    for wave in waves:
        wave.render()

    display.refresh()
    now_time = time.perf_counter() - start
