import pmma, time
from typing import List

display = pmma.Display()
display.create([1920, 1080], fullscreen=False)

circles: List[pmma.Shapes2D.Circle] = []
for x in range(5, 1920, 10):
    for y in range(5, 1080, 10):
        circle = pmma.Shapes2D.Circle()
        circle.shape_center.set_coord([x, y])
        circle.shape_color.configure(seed=0)
        circle.shape_color.generate_from_random(generate_alpha=False)
        circle.set_radius(4)
        circles.append(circle)

while True:
    display.clear()

    timer = time.perf_counter()

    for circle in circles:
        circle.render()

        position = circle.shape_center.get_coord()
        circle.shape_color.generate_from_3D_perlin_noise(
            (position[0] / 500),
            (position[1] / 500),
            (timer / 2),
            generate_alpha=False)

    display.continuous_refresh()