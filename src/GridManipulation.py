#type: ignore
import pmma
from typing import Iterable

display = pmma.Display()
display.create([1920, 1080], fullscreen=True)

seed = pmma.PerlinNoise()

x = 0

N = 10

circles: Iterable[pmma.Shapes2D.Circle] = []
for row in range(0, 1920, N):
    for column in range(0, 1080, N):
        circle = pmma.Shapes2D.Circle()
        circle.set_radius(4)
        circle.shape_color.configure(seed=0)
        circles.append(circle)

while True:
    display.clear()

    index = 0

    width = display.get_width()
    half_width = width/2
    height = display.get_height()
    half_height = height / 2

    for row in range(0, 1920, N):
        v = (row + x) / 1000 # 2000
        z = row / 1000
        k = x / 1000
        for column in range(0, 1080, N):
            r = int((width  / 2) * (1 + seed.noise_2d(v, column/2000)))
            c = int((height / 2) * (1 + seed.noise_2d(column/2000, v)))
            circles[index].shape_center.set_coord(r, c)
            circles[index].shape_color.generate_from_2D_perlin_noise(k, z)
            circles[index].render()
            index += 1

    x += 10.304891701056123

    display.continuous_refresh()