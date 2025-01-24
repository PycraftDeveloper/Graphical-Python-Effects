import pmma
import math

pmma.init()

display = pmma.Display()
display.create()

events = pmma.Events()

noise = pmma.Perlin()

circles = []
for _ in range(750): # 750
    circle = pmma.RadialPolygon()
    circle.set_radius(10)
    circle.generate_random_color()
    circles.append(circle)

offset = 0

def pythag(x, y):
    return math.sqrt((x*x)+(y*y))

ROOT_TWO = 2**0.5

while pmma.get_application_running():
    events.handle()

    display.clear()

    for i in range(len(circles)):
        a = ((1/360)*i)
        pos = [(math.sin(i+offset)*a)/display.get_aspect_ratio(), math.cos(i+offset)*a]
        distance = pythag(abs(pos[0]), abs(pos[1])) - circle.get_radius(format=pmma.Constants.OPENGL_COORDINATES)
        if distance < ROOT_TWO:
            size = noise.generate_1D_perlin_noise(-distance + pmma.get_application_run_time(), new_range=[1, 50]) * (distance / ROOT_TWO)
            size = max(size, 1)
            circles[i].set_radius(size)
            circles[i].set_center(pos, format=pmma.Constants.OPENGL_COORDINATES)
            circles[i].render()

    pmma.compute()
    display.refresh()

pmma.quit()