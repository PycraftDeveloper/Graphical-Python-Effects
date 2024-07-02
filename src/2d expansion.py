import pmma
import time
import pygame

pmma.init()

x_noise = pmma.Perlin()
y_noise = pmma.Perlin()
r_noise = pmma.Perlin()
g_noise = pmma.Perlin()
b_noise = pmma.Perlin()

display = pmma.Display()
display.create(1280, 720, fullscreen=True)

events = pmma.Events()

draw = pmma.Draw(canvas=display)

backpack = pmma.Backpack

math = pmma.Math()

class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def render(self):
        draw.circle(self.color, (self.x, self.y), self.radius)
        self.radius += 10

render_pipeline = []

start = time.perf_counter()
now_time = 0
while backpack.running:
    display.clear(pygame.transform.average_color(display.surface))
    events.handle()

    col = [r_noise.generate_1D_perlin_noise(now_time/7, range=[0, 255]),
            g_noise.generate_1D_perlin_noise(now_time/7, range=[0, 255]),
            b_noise.generate_1D_perlin_noise(now_time/7, range=[0, 255])]

    c = Circle(x_noise.generate_1D_perlin_noise(now_time/4, range=[50, display.get_width()-50]), y_noise.generate_1D_perlin_noise(now_time/4, range=[50, display.get_height()-50]), 100, col)
    render_pipeline.append(c)
    for element in render_pipeline:
        element.render()
        if element.radius > display.get_width():
            render_pipeline.remove(element)

    display.refresh()
    now_time = time.perf_counter() - start