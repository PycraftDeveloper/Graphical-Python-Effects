import pygame
import pmma
import time
import random

pygame.init()
pmma.init()

now_time = 0
display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
seed = random.randint(0, 1000000)
max_lifetime = 0

class Line:
    def __init__(self, x_pos):
        global max_lifetime
        self.x_noise = pmma.Perlin(seed=seed)
        self.y_noise = pmma.Perlin(seed=seed)
        self._x_pos = x_pos
        self.point = [x_pos, display.get_height() // 2]
        self.lifetime = random.randint(10, 30)
        max_lifetime = max(max_lifetime, self.lifetime)
        color = pmma.ColorConverter()
        self.color = color.generate_random_color()

    def render(self):
        pygame.draw.circle(display, self.color, self.point, 5 * (1-(now_time / self.lifetime)))
        self.point[0] += self.x_noise.generate_2D_perlin_noise(self._x_pos / 2000, now_time / 10, new_range=[-2, 2])
        self.point[1] += self.y_noise.generate_2D_perlin_noise(self._x_pos / 2000, -now_time / 10, new_range=[-2, 2])

lines = []
for x in range(0, display.get_width(), 10):
    lines.append(Line(x))

s = time.perf_counter()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            pmma.quit()
            quit()

    #display.fill((0, 0, 0))

    if now_time > max_lifetime:
        seed = random.randint(0, 1000000)
        max_lifetime = 0
        now_time = 0
        s = time.perf_counter()
        display.fill((0, 0, 0))
        lines = []
        for x in range(0, display.get_width(), 10):
            lines.append(Line(x))

    for line in lines:
        line.render()

    pygame.display.update()
    clock.tick(60)

    now_time = time.perf_counter() - s