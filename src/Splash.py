#type: ignore

import pmma, random

display = pmma.Display()
display.create([1920, 1080], fullscreen=False)

class Splash:
    def __init__(self):
        self.position = [random.randint(0, display.get_width()), random.randint(0, display.get_height())]
        self.radius = random.randint(5, 50)
        self.current_radius = 1
        self.current_width = self.radius
        color_converter = pmma.ColorConverter()
        color_converter.generate_random_color()
        self.color = color_converter.get_color_small_rgb()
        self.circle = pmma.Shapes2D.RadialPolygon()
        self.circle.set_centre(self.position)
        self.circle.set_color([*self.color, 1.0])
        self.mode = 0
        self.destroy = False

    def render(self):
        if self.mode == 0:
            if self.current_radius < self.radius:
                self.current_radius += 1
                self.circle.set_radius(self.current_radius)
            else:
                self.mode = 1
        else:
            if self.current_width > 0:
                self.current_width -= 1
                self.circle.set_width(self.current_width)
            else:
                self.destroy = True

        if self.current_width > 0:
            self.circle.render()

circles = []
for i in range(100):
    circles.append(Splash())

while True:
    destroyed = 0
    display.clear()

    for circle in circles:
        circle.render()

    display.continuous_refresh()

    for circle in circles:
        if circle.destroy:
            circles.remove(circle)
            destroyed += 1

    for i in range(destroyed):
        circles.append(Splash())