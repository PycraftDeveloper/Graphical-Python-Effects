import pmma
import time
import pygame
import traceback

pmma.init(log_information=True)

noise = pmma.Perlin()
r_noise = pmma.Perlin()
g_noise = pmma.Perlin()
b_noise = pmma.Perlin()

display = pmma.Display()
display.create(fullscreen=False, resizable=True)

events = pmma.Events()

draw = pmma.Draw()

backpack = pmma.Backpack

math = pmma.Math()

scale = 4

class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def render(self):
        draw.circle(self.color, (self.x, self.y), self.radius)
        self.radius += 10/scale

render_pipeline = []

start = time.perf_counter()
now_time = 0
while backpack.running:
    #print(display.get_fps())
    display.clear(pygame.transform.average_color(display.pygame_surface.pygame_surface))
    events.handle()

    col = [r_noise.generate_1D_perlin_noise(now_time/7, new_range=[0, 255]),
            g_noise.generate_1D_perlin_noise(now_time/7, new_range=[0, 255]),
            b_noise.generate_1D_perlin_noise(now_time/7, new_range=[0, 255])]

    c = Circle(display.get_width() // 2, noise.generate_1D_perlin_noise(now_time/4, new_range=[50, display.get_height()-50]), 100, col)
    render_pipeline.append(c)
    copy = render_pipeline.copy()
    for element in copy:
        element.render()
        if element.radius > display.get_width():
            render_pipeline.remove(element)

    pmma.compute()
    display.refresh(refresh_rate=75) # 7
    now_time = (time.perf_counter() - start)/scale

pmma.quit()