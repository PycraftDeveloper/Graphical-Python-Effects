import pmma

pmma.init()

display = pmma.Display()
display.create()

events = pmma.Events()

color_gen = pmma.ColorConverter()

class Lines:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.line = pmma.Line()
        self.line.set_start((x, y))
        self.x_noise = pmma.Perlin(seed=0)
        self.y_noise = pmma.Perlin(seed=0)
        self.line.set_width(3)

    def draw(self, color):
        x_end_pos = self.x_noise.generate_1D_perlin_noise(self.x/750+pmma.get_application_run_time(), new_range=[-50, 50])
        y_end_pos = self.y_noise.generate_1D_perlin_noise(self.y/750+pmma.get_application_run_time(), new_range=[-50, 50])
        self.line.set_end((self.x + x_end_pos, self.y + y_end_pos))
        self.line.set_color(color)
        self.line.render()

lines = []
for x in range(0, 1920, 50):
    for y in range(0, 1080, 50):
        lines.append(Lines(x, y))

while pmma.get_application_running():
    display.clear([0, 0, 0])

    events.handle()

    color = color_gen.generate_color_from_perlin_noise(pmma.get_application_run_time())

    for line in lines:
        line.draw(color)

    pmma.compute()
    display.refresh()