import time
import pygame
import pmma
import random

pmma.init()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

class Pane:
    def __init__(self):
        self.noise = pmma.Perlin()
        self.points = []
        self.surface = pygame.Surface((display.get_width(), display.get_height()))
        self.r_diff = random.randint(-20, 20)
        self.g_diff = random.randint(-20, 20)
        self.b_diff = random.randint(-20, 20)


    def render(self, col):
        col = [col[0]+self.r_diff, col[1]+self.g_diff, col[2]+self.b_diff]
        if col[0] > 255:
            col[0] = 255
        elif col[0] < 0:
            col[0] = 0

        if col[1] > 255:
            col[1] = 255
        elif col[1] < 0:
            col[1] = 0

        if col[2] > 255:
            col[2] = 255
        elif col[2] < 0:
            col[2] = 0

        self.surface.fill([0, 0, 0])
        if len(self.points) > display.get_width():
            del self.points[0]
        self.points.append(self.noise.generate_1D_perlin_noise(now_time/30, new_range=[0, display.get_height()]))

        points = [(0, display.get_height())]
        for i, point in enumerate(self.points):
            points.append((i, point))
        points.append((display.get_width(), display.get_height()))

        if len(points) > 5:
            pygame.draw.polygon(self.surface, col, points, 0)
        self.surface.set_colorkey([0, 0, 0])
        self.surface.set_alpha(100)
        display.blit(self.surface, (0, 0))

N = 5
panes = []
for _ in range(N):
    pane = Pane()
    panes.append(pane)

color = pmma.ColorConverter()
start = time.perf_counter()
now_time = 0
while True:
    #display.fill(pygame.transform.average_color(display))
    display.fill([255, 255, 255])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            pmma.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                pmma.quit()
                quit()

    generated_color = color.generate_color_from_perlin_noise(now_time/25, format=pmma.Constants.RGB)

    for pane in panes:
        pane.render(generated_color)

    pygame.display.flip()
    clock.tick(60)
    now_time = time.perf_counter() - start