try:
    import random
    import time
    import pmma
    import math
    from traceback import format_exception

    pmma.init(targeted_profile_application=True)

    canvas = pmma.Display()
    canvas.create(1280, 720, full_screen=False, resizable=True)
    events = pmma.Events()

    N = 1000

    s = int((canvas.get_width()**2 + canvas.get_height()**2)**0.5)

    class Particle:
        def __init__(self, n):
            self.n = n
            self.o = random.randint(500, s)
            self.pixel = pmma.Pixel()

        def __del__(self):
            self.pixel.quit()

        @pmma.profile_this
        def render(self, now_time, col):
            x = (canvas.get_width() - (math.sin(now_time+self.n) * self.o))/2
            y = (canvas.get_height() - (math.cos(now_time+self.n) * self.o))/2

            self.pixel.set_color(col)
            self.pixel.set_position([x, y])

            self.pixel.render()

    particles = []

    for i in range(N):
        particles.append(Particle(i))

    color = pmma.ColorConverter()

    start = time.perf_counter()
    now_time = 0
    while pmma.get_application_running():
        canvas.clear([0, 0, 0])

        events.handle()

        col = color.generate_color(now_time/100)

        for particle in particles:
            particle.render(now_time, col)

        pmma.compute()
        canvas.refresh()

        now_time = (time.perf_counter() - start)/100
    pmma.quit()
except Exception as error:
    print("".join(
        format_exception(
            None,
            error,
            error.__traceback__)))