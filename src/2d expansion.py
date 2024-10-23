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
display.create(1920, 1080, full_screen=True)

events = pmma.Events()

backpack = pmma.Backpack

math = pmma.Math()

scale = 4

class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.circle = pmma.RadialPolygon()
        self.circle.set_point_count()

    def render(self):
        self.circle.set_center([self.x, self.y])
        self.circle.set_radius(self.radius)
        self.circle.set_color(self.color)
        self.circle.render()
        self.radius += 10/scale

render_pipeline = []

start = time.perf_counter()
now_time = 0
while backpack.running:
    display.clear()
    events.handle()

    col = [r_noise.generate_1D_perlin_noise(now_time/7, new_range=[0, 255]),
            g_noise.generate_1D_perlin_noise(now_time/7, new_range=[0, 255]),
            b_noise.generate_1D_perlin_noise(now_time/7, new_range=[0, 255])]

    c = Circle(x_noise.generate_1D_perlin_noise(now_time/4, new_range=[50, display.get_width()-50]), y_noise.generate_1D_perlin_noise(now_time/4, new_range=[50, display.get_height()-50]), 100, col)
    render_pipeline.append(c)
    copy = render_pipeline.copy()
    for element in copy:
        element.render()
        if element.radius > display.get_width():
            render_pipeline.remove(element)

    display.refresh(refresh_rate=7)
    now_time = (time.perf_counter() - start)/scale