import pmma
import math
import random

pmma.init()

display = pmma.Display()
display.create(1920, 1080, fullscreen=True)

events = pmma.Events(display)

advmath = pmma.Math()

draw = pmma.Draw(display)

def degrees_to_radians(degrees):
    return ((360/N_POINTS) * degrees) * (math.pi / 180)

N_POINTS = 50
SPEED = 5
class Plane:
    def __init__(self):
        self.dirs = []
        self.mags = []

        for i in range(N_POINTS):
            x = degrees_to_radians(i)
            self.dirs.append([math.sin(x), math.cos(x)])
            self.mags.append(0)
        self.color = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]

    def compute(self):
        for _ in range(SPEED):
            index = random.randint(0, N_POINTS - 1)
            offset = 1+random.random()

            self.mags[index] += offset

        if min(self.mags) > advmath.pythag([display.get_width(), display.get_height()]):
            self.__init__()

    def render(self):
        points = []
        for i in range(len(self.dirs)):
            point = [self.dirs[i][0]*self.mags[i], self.dirs[i][1]*self.mags[i]]
            points.append([(display.get_width() - point[0])/2, (display.get_height() - point[1])/2])
        draw.polygon(self.color, points)

plane = Plane()

while True:
    events.handle()

    plane.compute()
    plane.render()

    display.refresh(refresh_rate=360)