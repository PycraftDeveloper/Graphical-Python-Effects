import pmma
import random
import pygame
import math
import time

canvas = pmma.Display()
canvas.create(1280, 720)

window_size = (1280, 720)
Surface = pygame.Surface(window_size).convert()
Surface.fill((0, 0, 0))

Surface.set_colorkey((0, 0, 0))

draw = pmma.Draw(canvas)

events = pmma.Events()
registry = pmma.Registry()

display_rect = pygame.Rect(0, 0, canvas.get_width(), canvas.get_height())

class Object:
    def __init__(self, radius=2):
        self.x = 0
        self.y = 0
        self.color = [0, 0, 0]
        self.radius = random.randint(500, canvas.get_width()*1.5)
        self.d = random.random()*math.pi*2


    def compute(self, time):
        self.x_pos = (canvas.get_width() - (math.sin(time + self.d) * self.radius))/2
        self.y_pos = (canvas.get_height() - (math.cos(time + self.d) * self.radius))/2
        self.radius += (random.random()*2)-1
        self.color = [
            int((100/(canvas.get_width()*1.5))*self.radius),
            int((50/(canvas.get_width()*1.5))*self.radius),
            int((255/(canvas.get_width()*1.5))*self.radius)]

    def render(self):
        try:
            #draw.circle(self.color, (self.x_pos, self.y_pos), 1)
            draw.pixel(self.color, (self.x, self.y))
        except Exception as error:
            pass

objects = []
for i in range(3000):
    objects.append(Object())

start = time.perf_counter()
now_time = 0
while registry.running:
    Surface.fill((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))
    #canvas.clear(0, 0, 0)

    events.handle(canvas)

    for object in objects:
        object.compute(now_time)
        object.render()

    Surface2.set_alpha(1) # 10
    canvas.blit(Surface2, (0, 0))
    canvas.blit(Surface, (0, 0))

    canvas.refresh()
    now_time = time.perf_counter() - start
