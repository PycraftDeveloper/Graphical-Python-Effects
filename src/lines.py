import pygame
import pmma
import time

pygame.init()
pmma.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

class Line:
    def __init__(self, y_pos):
        self._noise = pmma.Perlin(seed=0)
        self._y_pos = y_pos

    def render(self, col):
        points = []
        sf = 1920 / 600
        for x in range(600):
            points.append([x*sf, self._y_pos + self._noise.generate_2D_perlin_noise(now_time + (x*sf)/1000, self._y_pos/200, new_range=[-80, 80])])

        pygame.draw.lines(display, col, False, points, 3)

N = 50
y_pos = 0
lines = []
for i in range(N):
    lines.append(Line(y_pos))
    y_pos += 1080 / N

color = pmma.ColorConverter()
start = time.perf_counter()
now_time = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    col = color.generate_color(now_time/3)

    display.fill((0, 0, 0))

    for line in lines:
        line.render(col)

    pygame.display.update()
    clock.tick(60)
    print(clock.get_fps())
    now_time = time.perf_counter() - start