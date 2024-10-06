import pygame
import random
import pmma
import time

pmma.init()

x_noise = pmma.Perlin()
y_noise = pmma.Perlin()

color = pmma.ColorConverter()
r_noise = pmma.Perlin()
g_noise = pmma.Perlin()
b_noise = pmma.Perlin()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCALE = 1000

class Square:
    def __init__(self, x, y, size, color, dx, dy):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.dx = dx
        self.dy = dy
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def render(self):
        self.color = [
            r_noise.generate_2D_perlin_noise(self.x/SCALE + now_time/10, self.y/SCALE + now_time/10, new_range=[0, 255]),
            g_noise.generate_2D_perlin_noise(self.x/SCALE + now_time/10, self.y/SCALE + now_time/10, new_range=[0, 255]),
            b_noise.generate_2D_perlin_noise(self.x/SCALE + now_time/10, self.y/SCALE + now_time/10, new_range=[0, 255])
        ]
        if self.color != [0, 0, 0]:
            pygame.draw.rect(display, self.color, self.rect)

squares = []
linear_squares = []
dx = 0
for x in range(0, display.get_width(), 20):
    row = []
    dy = 0
    for y in range(0, display.get_height(), 20):
        sq = Square(x, y, 20, [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)], dx, dy)
        row.append(sq)
        linear_squares.append(sq)
        dy += 1
    squares.append(row)
    dx += 1

clock = pygame.time.Clock()

start = time.perf_counter()
now_time = 0
while True:
    display.fill([0, 0, 0])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    for square in linear_squares:
        square.render()

    clock.tick(12)
    pygame.display.update()
    now_time = -(time.perf_counter() - start)