# type: ignore

import pmma, math

display = pmma.Display()
display.create([1920, 1080], fullscreen=True)

UP = False
DOWN = True

class Circle(pmma.Shapes2D.Circle):
    def __init__(self, position) -> None:
        super().__init__()
        self.set_radius(50)
        self.shape_center.set_coord(*position)

        self.position = position

        height = display.get_height()

        self.color_div = 1 - (abs(2 * position[1] / height - 1) ** 0.6) # 0.5

        self.color = pmma.NumberFormats.Color()
        self.color.configure(seed=0)

    def render(self):
        self.color.generate_from_2D_perlin_noise(pmma.General.get_application_run_time(), self.position[0]/1000)
        base_color = self.color.get_rgb()

        # Blend between black → base_color → white
        if self.color_div < 0.5:
            # Blend from black to base color
            factor = self.color_div * 2  # 0 to 1
            r = base_color[0] * factor
            g = base_color[1] * factor
            b = base_color[2] * factor
        else:
            # Blend from base color to white
            factor = (self.color_div - 0.5) * 2  # 0 to 1
            r = base_color[0] + (1 - base_color[0]) * factor
            g = base_color[1] + (1 - base_color[1]) * factor
            b = base_color[2] + (1 - base_color[2]) * factor
        self.shape_color.set_rgb(r, g, b)
        super().render()

circles = []

padding = display.get_width() / 200

direction = True
for x in range(0, display.get_width(), 100):
    if direction:
        order = (0, display.get_height())
    else:
        order = (display.get_height(), 0, -1)

    for y in range(*order):
        circle = Circle((x + padding, y))
        circles.append(circle)
    direction = not direction

while pmma.General.is_application_running():
    display.clear()

    for circle in circles:
        circle.render()

    display.continuous_refresh()