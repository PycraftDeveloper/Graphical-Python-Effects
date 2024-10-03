import pmma
import time

pmma.init()

x_noise = pmma.Perlin()
y_noise = pmma.Perlin()

display = pmma.Display()
display.create()

events = pmma.Events()

circ = pmma.RadialPolygon()
circ.set_radius(5)
circ.set_color([255, 255, 255])

start = time.perf_counter()
now_time = 0
while pmma.Backpack.running:
    events.handle()

    circ.set_center([x_noise.generate_1D_perlin_noise(now_time), y_noise.generate_1D_perlin_noise(now_time)], pmma.Constants.OPENGL_COORDINATES)

    circ.render()

    pmma.compute()
    display.refresh()
    now_time = time.perf_counter() - start

pmma.quit()