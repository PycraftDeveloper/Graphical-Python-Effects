
import random
import time
import pmma
import pygame
import math

pmma.init()

canvas = pmma.Display()
canvas.create(1920, 1080, full_screen=True)
events = pmma.Events()

color_perlin = pmma.Perlin(random.randint(0, 9999))
rotation_perlin = pmma.Perlin(random.randint(0, 9999))

class Square:
    def __init__(self, n):
        self.n = n/10
        self.size = n
        self.iter = n

        self.rectangle = pmma.Rectangle()
        self.rectangle.set_center((0, 0), pmma.Constants.OPENGL_COORDINATES)
        self.rectangle.set_size((self.size, self.size))
        self.color = pmma.ColorConverter(seed=0)

    def render(self, now_time):
        self.rectangle.set_rotation(self.n)
        self.rectangle.set_color(self.color.generate_color_from_perlin_noise((now_time+self.n)/75, format=pmma.Constants.RGB))

        self.rectangle.render()

        self.n += 0.01

squares = []
diag = int(math.sqrt(canvas.get_width()**2 + canvas.get_width()**2))
for i in range(0, diag, 8):
    squares.append(Square(diag-i))

print(i)

start = time.perf_counter()
now_time = 0
while True:
    #k = time.perf_counter()
    center = (canvas.get_width()/2, canvas.get_height()/2)

    canvas.clear()

    events.handle(canvas)

    for square in squares:
        square.render(now_time)

    pmma.compute()
    canvas.refresh()
    now_time = time.perf_counter() - start
    #s = time.perf_counter()
