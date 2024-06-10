import random
import pygame

import pmma

pmma.init()

display = pmma.Display()
display.create(1920, 1080, fullscreen=True)

events = pmma.Events(display)

draw = pmma.Draw(display)

seed = pmma.Perlin()
seedr = pmma.Perlin()
seedg = pmma.Perlin()
seedb = pmma.Perlin()

x = 0

N = 10

do_screen_clearing = 0
while pmma.Registry.running:
    event_arr = events.handle(return_events=True)
    for event in event_arr:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                x += random.randint(100, 99999)
            else:
                do_screen_clearing += 1

    if do_screen_clearing == 0:
        display.clear(0, 0, 0)

    if do_screen_clearing == 1:
        window_size = display.get_size()

        Surface = pygame.Surface(window_size).convert()
        Surface.fill((0, 0, 0))

        Surface.set_colorkey((0, 0, 0))
        Surface2 = pygame.Surface(window_size)

        Surface2.fill((0, 0, 0))

    do_screen_clearing = do_screen_clearing % 3

    for row in range(0, display.get_width(), N):
        color = [
                seedr.generate_2D_perlin_noise(x/100, row/1000, range=[0, 255]),
                seedg.generate_2D_perlin_noise(x/100, row/1000, range=[0, 255]),
                seedb.generate_2D_perlin_noise(x/100, row/1000, range=[0, 255])]

        for column in range(0, display.get_height(), N):
            r = display.get_width()/2 + int(row*seed.generate_2D_perlin_noise((row+x)/2000, column/2000))
            c = display.get_height()/2 + int(column*seed.generate_2D_perlin_noise(column/2000, (row+x)/2000))
            if do_screen_clearing == 1:
                pygame.draw.circle(Surface, color, (int(r), int(c)), 1)
            else:
                draw.circle(color, (int(r), int(c)), 1) # 10 is a good size

    x += 10.304891701056123

    if do_screen_clearing == 1:
        Surface2.set_alpha(10) # 10

        display.blit(Surface2, (0, 0))

        display.blit(Surface, (0, 0))

    display.refresh()