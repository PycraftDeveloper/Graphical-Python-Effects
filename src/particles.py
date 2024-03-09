from traceback import format_exception
try:
    import random
    import time
    import pmma
    import pygame.gfxdraw as gfxdraw
    import math

    canvas = pmma.Canvas()
    canvas.create_canvas(1280, 720)
    events = pmma.Events()

    registry = pmma.Registry

    N = 10_000
    X = random.randint(0, 10000)
    Y = random.randint(0, 10000)
    K = random.randint(0, 10000)

    x_velocity_perlin = pmma.Perlin(X)
    y_velocity_perlin = pmma.Perlin(Y)
    perlin_pos = pmma.Perlin(K)

    def center_origin(surf, p):
        return (p[0] + surf.get_width() // 2, p[1] + surf.get_height() // 2)

    s = int((canvas.get_width()**2 + canvas.get_height()**2)**0.5)

    class Particle:
        def __init__(self, n):
            self.n = n
            self.o = random.randint(500, s)

        def render(self, now_time, col):

            x = (canvas.get_width() - (math.sin(now_time+self.n) * self.o))/2
            y = (canvas.get_height() - (math.cos(now_time+self.n) * self.o))/2

            gfxdraw.pixel(canvas.display, int(x), int(y), col)

    particles = []

    for i in range(N):
        particles.append(Particle(i))

    start = time.perf_counter()
    now_time = 0
    while registry.running:
        canvas.clear(0, 0, 0)

        events.handle(canvas)

        col = [
            perlin_pos.generate_2D_perlin_noise(now_time/100, 0, range=[0, 255]),
            perlin_pos.generate_2D_perlin_noise(0, now_time/100, range=[0, 255]),
            perlin_pos.generate_2D_perlin_noise(-now_time/100, -now_time/100, range=[0, 255])]

        for particle in particles:
            particle.render(now_time, col)

        canvas.refresh()
        now_time = (time.perf_counter() - start)/100
except Exception as error:
    print("".join(
        format_exception(
            None,
            error,
            error.__traceback__)))