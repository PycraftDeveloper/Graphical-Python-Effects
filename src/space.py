import pygame
import math
import time
import random

import pmma

#pmma.set_display_mode(pmma.Constants.PYGAME)

try:
    pmma.init()
except Exception as e:
    import traceback
    traceback.print_exc()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
r_noise = pmma.Perlin()
g_noise = pmma.Perlin()
b_noise = pmma.Perlin()
advmath = pmma.Math()
CULL_DIAMETER = advmath.pythag(display.get_size())

class Point:
    def __init__(self):
        self.x = display.get_width()/2
        self.y = display.get_height()/2
        self.offset = random.random() * 100
        self.spin_offset = random.random() * 2 * math.pi
        self.orbit = self.offset
        self.escaped = False
        self.width = 0
        self.noise = pmma.Perlin()
        self.r_delta = random.randint(-20, 20)
        self.g_delta = random.randint(-20, 20)
        self.b_delta = random.randint(-20, 20)

    def render(self, color):
        if self.escaped is False:
            if self.orbit >= 75:
                self.orbit += random.random()
            elif self.orbit < 75:
                self.orbit += 3
                self.width = (3 / 75) * self.orbit

            if self.orbit >= 100:
                self.escaped = True
        else:
            self.orbit += 7
        x = math.sin(self.spin_offset + now_time) * self.orbit + self.x
        y = math.cos(self.spin_offset + now_time) * self.orbit + self.y
        if self.orbit * 2 > CULL_DIAMETER:
            self.__init__()
        if self.orbit >= 0:
            if self.width > 0:
                luminosity = self.noise.generate_1D_perlin_noise(now_time, new_range=[0.75, 1.25])
                r = self.r_delta + color[0] * luminosity
                if r > 255: r = 255
                if r < 0: r = 0
                g = self.g_delta + color[1] * luminosity
                if g > 255: g = 255
                if g < 0: g = 0
                b = self.b_delta + color[2] * luminosity
                if b > 255: b = 255
                if b < 0: b = 0
                color = [r, g, b]
                pygame.draw.circle(display, color, (x, y), self.width)

points = []
N = 4500
for i in range(N):
    points.append(Point())

start = time.perf_counter()
now_time = 0
color = [255, 255, 255]
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    display.fill([0, 0, 0])

    color = [
        r_noise.generate_2D_perlin_noise(now_time/10, 0, new_range=[0, 255]),
        g_noise.generate_2D_perlin_noise(now_time/10, 0, new_range=[0, 255]),
        b_noise.generate_2D_perlin_noise(now_time/10, 0, new_range=[0, 255])
    ]

    for point in points:
        point.render(color)

    pygame.display.flip()
    #if clock.get_fps() < 60:
        #print("SLOW", clock.get_fps())
    clock.tick(60)
    now_time = time.perf_counter() - start
    pmma.Registry.in_game_loop = True