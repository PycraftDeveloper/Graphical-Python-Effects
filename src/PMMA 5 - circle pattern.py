import pmma, random, time

display = pmma.Display()
display.create([1920, 1080], fullscreen=False, vsync=True)

circles = []

class Circle:
    def __init__(self):
        self.c = pmma.Shapes2D.RadialPolygon()
        self.r = random.randint(5, 20)
        self.c.set_radius(self.r)
        self.color = pmma.ColorConverter()
        self.color.generate_color_from_perlin_noise(time.perf_counter())
        self.c.set_color([*self.color.get_color_small_rgb(), 0.8])
        self.position = [1920/2, 1080]
        self.boost = 2 * random.random() * 4
        self.velocity = [((random.random() - 0.5)*2)*2.75, -random.random() * self.boost]
        self.duration = time.perf_counter()

    def render(self):
        self.c.set_centre(self.position)

        self.c.render()

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1] + (time.perf_counter()-self.duration)**2

for i in range(1000):
    circles.append(Circle())

while True:
    display.clear()

    for i in range(len(circles)):
        circles[i].render()

        if circles[i].position[1] > 1080:
            circles[i] = Circle()

    display.continuous_refresh()