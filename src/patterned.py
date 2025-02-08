import pmma
import math
import random

pmma.set_clean_profiling(False)
pmma.set_profile_result_path(r"H:\Downloads\twtwo profile.txt")
#pmma.init(general_profile_application=True)
pmma.init(general_profile_application=False, use_c_acceleration=True)

display = pmma.Display()
display.create(vsync=False)

events = pmma.Events()

noise = pmma.Perlin()

circles = []
for _ in range(750): # 750
    circle = pmma.RadialPolygon()
    circle.set_radius(10)
    circle.generate_random_color()
    circle.set_center((0, 0), pmma.Constants.OPENGL_COORDINATES)
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
            size = noise.generate_1D_perlin_noise(-distance + pmma.get_application_run_time()/2, new_range=[1, 50]) * (distance / ROOT_TWO)
            size = max(size, 1)
            circles[i].set_radius(size)
            circles[i].set_center(pos, format=pmma.Constants.OPENGL_COORDINATES)

    for i in range(len(circles)):
        if random.choice([True, False]):
            #circles[i].generate_random_color()
            circles[i].render()

    pmma.compute()

    display.refresh(lower_refresh_rate_when_minimized=False, lower_refresh_rate_when_unfocused=False, refresh_rate=6000)

pmma.quit()