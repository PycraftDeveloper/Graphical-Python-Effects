import pmma
import random
import time

pmma.init()

display = pmma.Display()
display.create()

events = pmma.Events()

registry = pmma.Registry

color = pmma.Color()

class Point:
    def __init__(self):
        self.x = random.randint(0, display.get_width())
        self.y = random.randint(0, display.get_height())

        self.noise = pmma.Perlin()

        self.circle = pmma.Circle()
        self.circle.set_radius(3)

    def compute(self):
        x_value = self.noise.generate_1D_perlin_noise(now_time/10 + self.x)
        y_value = self.noise.generate_1D_perlin_noise(now_time/10 + self.y)

        if x_value > 0.5:
            self.x += 1
        elif x_value < -0.5:
            self.x -= 1

        if y_value > 0.5:
            self.y += 1
        elif y_value < -0.5:
            self.y -= 1

        if self.x < 0:
            self.x = random.randint(0, display.get_width())
            self.y = random.randint(0, display.get_height())

        elif self.x > display.get_width():
            self.x = random.randint(0, display.get_width())
            self.y = random.randint(0, display.get_height())

        if self.y < 0:
            self.x = random.randint(0, display.get_width())
            self.y = random.randint(0, display.get_height())

        elif self.y > display.get_height():
            self.x = random.randint(0, display.get_width())
            self.y = random.randint(0, display.get_height())

    def render(self, color):
        self.compute()

        self.circle.set_center([self.x, self.y])
        self.circle.set_color(color)

        self.circle.draw()

N = 720
points = [Point() for _ in range(N)]

start = time.perf_counter()
now_time = 0
while registry.running:
    color_value = color.generate_color_from_perlin_noise(now_time/10, format=pmma.Constants.RGB)

    display.clear()

    events.handle()

    for point in points:
        point.render(color_value)

    pmma.compute()

    display.refresh()

    now_time = time.perf_counter() - start

pmma.quit()