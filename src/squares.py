
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
        self.rectangle.set_red_seed(0)
        self.rectangle.set_green_seed(1)
        self.rectangle.set_blue_seed(2)
        self.rectangle.set_alpha_seed(3)
        self.rectangle.generate_color_from_perlin_noise()

    def render(self, now_time):
        self.rectangle.set_rotation(self.n)
        self.rectangle.generate_color_from_perlin_noise((now_time+self.n)/75, generate_alpha=False)

        self.rectangle.render()

        self.n += 0.01

squares = []
diag = int(math.sqrt(canvas.get_width()**2 + canvas.get_width()**2))
for i in range(0, diag, 8):
    squares.append(Square(diag-i))

start = time.perf_counter()
now_time = 0
while pmma.get_application_running():
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

pmma.quit()
