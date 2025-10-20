#type: ignore
import pmma, time, random, math

display = pmma.Display()
display.create((1920, 1080))

core = pmma.Shapes2D.Circle()
core.set_radius(100)
core.shape_center.set_coord(*display.get_center())

color = pmma.NumberFormats.Color()
color.configure()
color.generate_from_1D_perlin_noise(time.perf_counter())

size = display.get_size()
dist = (((display.get_width() ** 2) + (display.get_height() ** 2)) ** 0.5) / 2
angles = {}
rays = []

class Ray:
    def __init__(self, angle, i):
        self.angle = angle
        if random.randint(0, 1) == 0:
            self.length = 6
        else:
            self.length = random.randint(7, 100)
        self.velocity = 2.0
        self.origin = display.get_center()
        self.distance = 0.0

        self.line = pmma.Shapes2D.Line()
        self.line.shape_color.set_RGB(*color.get_RGB())
        self.line.set_width(3)

        self.i = i
        self.has_unlocked = False

        self.c_end = [0, 0]

    def render(self):
        if self.distance > dist:
            rays.remove(self)
            return

        if not self.has_unlocked and self.distance > self.length * 1.5:
            angles[self.i] = False
            self.has_unlocked = True

        self.distance += self.velocity

        dx = math.cos(self.angle)
        dy = math.sin(self.angle)

        start_x = self.origin[0] + dx * self.distance
        start_y = self.origin[1] + dy * self.distance
        end_x = start_x + dx * self.length
        end_y = start_y + dy * self.length
        self.c_end = [end_x, end_y]

        self.line.shape_start.set_coord(start_x, start_y)
        self.line.shape_end.set_coord(end_x, end_y)

        self.line.render()

for angle in range(0, 360, 3):
    if random.randint(0, 10) == 0:
        rays.append(Ray(math.radians(angle), angle))
        angles[angle] = True
    else:
        angles[angle] = False

while True:
    color.generate_from_1D_perlin_noise(time.perf_counter()/2.5)

    display.clear()

    for ray in rays:
        ray.render()

    for i in range(0, 360, 3):
        if angles[i] is False:
            if random.randint(0, 10) == 0:
                rays.append(Ray(math.radians(i), i))
                angles[i] = True

    core.shape_color.set_RGB(*color.get_RGB())
    core.render()

    display.continuous_refresh()