import pmma
import math
import random
import time

from pmma.bin import perlin_noise

pmma.init()

display = pmma.Display()
display.create(1920, 1080, fullscreen=True)

events = pmma.Events(display)

advmath = pmma.Math()

draw = pmma.Draw(display)

def degrees_to_radians(degrees):
    return ((360/N_POINTS) * degrees) * (math.pi / 180)

N_POINTS = 500
SPEED = 5
class Plane:
    def __init__(self):
        self.dirs = []
        self.mags = []
        self.noise = perlin_noise.PerlinNoise(0, 1, 1)

        for i in range(N_POINTS):
            x = degrees_to_radians(i)
            self.dirs.append([math.sin(x), math.cos(x)])
            self.mags.append(0)
        self.color = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]

    def compute(self, now_time):
        for index in range(len(self.mags)):
            x, y = self.dirs[index][0]*self.mags[index], self.dirs[index][1]*self.mags[index]
            self.mags[index] = 500+self.noise.fBM2D((x/5+now_time/1)/50, (y/5+now_time/1)/50)*300

        if min(self.mags) > advmath.pythag([display.get_width(), display.get_height()]):
            self.__init__()

    def render(self):
        points = []
        for i in range(len(self.dirs)):
            point = [self.dirs[i][0]*self.mags[i], self.dirs[i][1]*self.mags[i]]
            points.append([(display.get_width() - point[0])/2, (display.get_height() - point[1])/2])
        draw.polygon(self.color, points, width=1)

plane = Plane()

start = time.perf_counter()
now_time = 0
while True:
    display.clear()
    events.handle()

    plane.compute(now_time)
    plane.render()

    display.refresh()
    now_time = time.perf_counter() - start