import pmma
import pygame
from pygame import gfxdraw
import random

canvas = pmma.Canvas()
canvas.create_canvas(1280, 720)
registry = pmma.Registry()
events = pmma.Events()

class Point():
    def __init__(self, x, color):
        self.y = canvas.get_height()/2
        self.dir_y = random.choice([-1, 1])
        self.x = x
        self.color = color
        self.magnitude = random.random()

    def compute(self):
        self.y += self.dir_y * self.magnitude

        self.color = [self.color[0]-self.magnitude, self.color[1]-self.magnitude, self.color[2]-self.magnitude]

        if self.color[0] <= 0:
            self.color[0] = 0
        if self.color[1] <= 0:
            self.color[1] = 0
        if self.color[2] <= 0:
            self.color[2] = 0

        if sum(self.color) == 0:
            random_x_pos = random.randint(0, canvas.get_width())
            random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.__init__(random_x_pos, random_color)

    def render(self):
        gfxdraw.pixel(canvas.display, int(self.x), int(self.y), self.color)

points = []

for _ in range(20_000):
    random_x_pos = random.randint(0, canvas.get_width())
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    point = Point(random_x_pos, random_color)
    points.append(point)

while registry.running:
    canvas.clear(0, 0, 0)

    list_of_events = events.handle(canvas)
    for event in list_of_events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                points = []
                for _ in range(20_000):
                    random_x_pos = random.randint(0, canvas.get_width())
                    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    point = Point(random_x_pos, random_color)
                    points.append(point)

    for point in points:
        point.compute()
        point.render()

    canvas.refresh()