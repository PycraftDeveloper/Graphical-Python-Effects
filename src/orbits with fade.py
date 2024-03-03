import math
import time
import random

import pygame

pygame.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN, vsync=1)

clock = pygame.time.Clock()

start = time.perf_counter()

class Planet():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.r = random.randint(1, 20)
        self.d = random.randint(1,display.get_height()/2)
        self.color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.s = random.random()

    def render(self):
        self.x = c[0] + self.d * math.sin(d*self.s)
        self.y = c[1] + self.d * math.cos(d*self.s)
        pygame.draw.circle(display, self.color, (self.x, self.y), self.r)

p = []
for _ in range(20):
    p.append(Planet())

while True:
    d = time.perf_counter()-start
    c = display.get_width() / 2, display.get_height() / 2
    window_size = display.get_width(), display.get_height()

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

            if event.key == pygame.K_SPACE:
                display.fill([0, 0, 0])

    for object in p:
        object.render()

    Surface2.set_alpha(1) # 10

    display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)