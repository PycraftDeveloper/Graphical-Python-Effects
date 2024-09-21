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
        self._points = []

    def render(self, col):
        C = 750
        filled = False
        points = []
        self._points.append(self._y_pos + self._noise.generate_2D_perlin_noise(now_time/5, self._y_pos/200, new_range=[-80, 80]))
        lx = 0
        for x in range(len(self._points)):
            points.append([lx, self._points[x]])
            lx = (1920 / len(self._points))*x

        if len(self._points) > C:
            del self._points[0]
            filled = True

        try:
            pygame.draw.lines(display, col, False, points, 3)
        except:
            pass
        return filled

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
        f = line.render(col)

    pygame.display.update()
    if f:
        clock.tick(60)
    else:
        clock.tick(2000)
    now_time = time.perf_counter() - start