import pmma

pmma.init()

pmma.set_allow_anti_aliasing(True)
pmma.set_anti_aliasing_level(8)

display = pmma.Display()
display.create((1920, 1080), full_screen=True)

events = pmma.Events()

class Color:
    def __init__(self):
        self.r = pmma.Perlin()
        self.g = pmma.Perlin()
        self.b = pmma.Perlin()

    def generate_color_from_perlin_noise(self, x_value=0, y_value=0):
        return self.r.generate_2D_perlin_noise(x_value, y_value, [0, 255]), self.g.generate_2D_perlin_noise(x_value, y_value, [0, 255]), self.b.generate_2D_perlin_noise(x_value, y_value, [0, 255])

color = Color()

class Circle:
    def __init__(self, x, y):
        self.circle = pmma.Circle()
        self.circle.set_radius(15)
        self.circle.set_center([x, y])
        self.position = [x/1000, y/1000]

    def render(self):
        time = pmma.get_application_run_time()
        self.circle.set_color(color.generate_color_from_perlin_noise(self.position[0] + time, self.position[1] + time), format=pmma.Constants.RGB)
        self.circle.render()

circles = []
for x in range(15, display.get_width(), 45):
    for y in range(15, display.get_height(), 45):
        circles.append(Circle(x, y))

while True:
    events.handle()

    display.clear()

    for circle in circles:
        circle.render()

    pmma.compute()

    display.refresh()