import pygame
import random
import pmma
import time

pmma.init()

x_noise = pmma.Perlin()
y_noise = pmma.Perlin()

color = pmma.ColorConverter()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

class Square:
    def __init__(self, x, y, size, color, dx, dy):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.dx = dx
        self.dy = dy

    def render(self, squares):
        self.gather_context(squares)
        if self.color != [0, 0, 0]:
            pygame.draw.rect(display, self.color, [self.x, self.y, self.size, self.size])

    def gather_context(self, squares):
        self.color = self.color
        x = 1

        try:
            if squares[self.dx-1][self.dy].color != [0, 0, 0]:
                self.color[0] += squares[self.dx-1][self.dy].color[0]
                self.color[1] += squares[self.dx-1][self.dy].color[1]
                self.color[2] += squares[self.dx-1][self.dy].color[2]
                x += 1
        except:
            pass

        try:
            if squares[self.dx+1][self.dy].color != [0, 0, 0]:
                self.color[0] += squares[self.dx+1][self.dy].color[0]
                self.color[1] += squares[self.dx+1][self.dy].color[1]
                self.color[2] += squares[self.dx+1][self.dy].color[2]
                x += 1
        except:
            pass

        try:
            if squares[self.dx][self.dy+1].color != [0, 0, 0]:
                self.color[0] += squares[self.dx][self.dy+1].color[0]
                self.color[1] += squares[self.dx][self.dy+1].color[1]
                self.color[2] += squares[self.dx][self.dy+1].color[2]
                x += 1
        except:
            pass

        try:
            if squares[self.dx][self.dy-1].color != [0, 0, 0]:
                self.color[0] += squares[self.dx][self.dy-1].color[0]
                self.color[1] += squares[self.dx][self.dy-1].color[1]
                self.color[2] += squares[self.dx][self.dy-1].color[2]
                x += 1
        except:
            pass

        self.color[0] /= x
        self.color[1] /= x
        self.color[2] /= x

        self.color[0] = int(self.color[0])
        self.color[1] = int(self.color[1])
        self.color[2] = int(self.color[2])

        if self.color[0] > 255:
            self.color[0] = 255
        if self.color[1] > 255:
            self.color[1] = 255
        if self.color[2] > 255:
            self.color[2] = 255

squares = []
linear_squares = []
dx = 0
for x in range(0, display.get_width(), 20):
    row = []
    dy = 0
    for y in range(0, display.get_height(), 20):
        sq = Square(x, y, 20, [0, 0, 0], dx, dy)
        row.append(sq)
        linear_squares.append(sq)
        dy += 1
    squares.append(row)
    dx += 1

clock = pygame.time.Clock()

x = 0
y = 0
start = time.perf_counter()
now_time = 0
while True:
    display.fill([0, 0, 0])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    x += x_noise.generate_1D_perlin_noise(now_time/100, new_range=[-1, 1])
    y += y_noise.generate_1D_perlin_noise(-now_time/100, new_range=[-1, 1])

    if x > len(squares)-1:
        x = 0
    if x < 0:
        x = len(squares)-1

    if y > len(squares[0])-1:
        y = 0
    if y < 0:
        y = len(squares[0])-1

    c = color.generate_color_from_perlin_noise(now_time, format=pmma.Constants.RGB, color_range=[0, 255])
    squares[int(x)][int(y)].color = c

    for square in linear_squares:
        square.render(squares)

    clock.tick(60)
    pygame.display.update()
    now_time = time.perf_counter() - start