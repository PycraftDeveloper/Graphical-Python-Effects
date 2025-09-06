# type: ignore

import pmma, time
import math

display = pmma.Display()
display.create([1920, 1080], fullscreen=True)

half_width = display.get_width() / 2
half_height = display.get_height() / 2

offset_noise = pmma.PerlinNoise()

class Circle(pmma.Shapes2D.Circle):
    def __init__(self, index, position) -> None:
        super().__init__()
        self.set_radius(5)
        self.position = position
        self.shape_center.set_coord(*position)

        self.dir = [
            (position[0] - half_width) / 100,
            (position[1] - half_height) / 100
        ]

        self.shape_color.configure(seed=index)

        self.shape_color.generate_from_1D_perlin_noise(time.perf_counter()/5, generate_alpha=False)

    def render(self):
        super().render()

        self.position[0] += self.dir[0]
        self.position[1] += self.dir[1]

        if self.position[0] < 0:
            return True
        if self.position[0] > display.get_width():
            return True

        if self.position[1] < 0:
            return True
        if self.position[1] > display.get_height():
            return True

        self.shape_center.set_coord(*self.position)

circles = []
offset = (1 + offset_noise.noise_1d(time.perf_counter() / 5)) * math.pi
for c in range(10):
    angle = (c / 10) * 2 * math.pi
    angle += offset

    x_position = half_width + (math.cos(angle) * 100)
    y_position = half_height + (math.sin(angle) * 100)

    circles.append(Circle(c, [x_position, y_position]))

while pmma.General.is_application_running():
    display.clear()

    gc = []
    index = 0
    for circle in circles:
        if circle.render():
            gc.append(index)
        index += 1

    for index in gc[::-1]:
        circles.pop(index)

    timer = time.perf_counter()
    offset = (1 + offset_noise.noise_1d(time.perf_counter() / 5)) * math.pi
    for c in range(10):
        angle = (c / 10) * 2 * math.pi
        angle += offset

        x_position = half_width + (math.cos(angle) * 100)
        y_position = half_height + (math.sin(angle) * 100)

        circles.append(Circle(c, [x_position, y_position]))

    display.continuous_refresh()