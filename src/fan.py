import pmma
import math
import random
import time
import pygame

from pmma.bin import perlin_noise

pmma.init()

display = pmma.Display()
display.create(1920, 1080, fullscreen=True)

events = pmma.Events(display)

advmath = pmma.Math()

draw = pmma.Draw(display)

delta = math.pi / 2

start = time.perf_counter()
now_time = 0
while True:
    #display.clear()
    events.handle()

    window_x, window_y = display.get_size()
    window_size = (window_x, window_y)

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))

    ###

    x = math.sin(now_time) * display.get_height()
    y = math.cos(now_time) * display.get_height()

    points = [(display.get_width()/2, display.get_height()/2), ((display.get_width() - x)/2, (display.get_height() - y)/2)]
    pygame.draw.line(Surface, (255, 0, 0), points[0], points[1], width=2)

    ###

    x = math.sin(now_time + delta) * display.get_height()
    y = math.cos(now_time + delta) * display.get_height()

    points = [(display.get_width()/2, display.get_height()/2), ((display.get_width() - x)/2, (display.get_height() - y)/2)]
    pygame.draw.line(Surface, (255, 0, 0), points[0], points[1], width=2)

    ###

    x = math.sin(now_time + delta*2) * display.get_height()
    y = math.cos(now_time + delta*2) * display.get_height()

    points = [(display.get_width()/2, display.get_height()/2), ((display.get_width() - x)/2, (display.get_height() - y)/2)]
    pygame.draw.line(Surface, (255, 0, 0), points[0], points[1], width=2)

    ###

    x = math.sin(now_time + delta*3) * display.get_height()
    y = math.cos(now_time + delta*3) * display.get_height()

    points = [(display.get_width()/2, display.get_height()/2), ((display.get_width() - x)/2, (display.get_height() - y)/2)]
    pygame.draw.line(Surface, (255, 0, 0), points[0], points[1], width=2)

    ###

    Surface2.set_alpha(1) # 10

    display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    display.refresh(refresh_rate=10000)
    now_time = time.perf_counter() - start