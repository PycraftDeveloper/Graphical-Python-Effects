import pmma
pmma.init()

import pygame
pygame.init()

import time

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

noise = pmma.Perlin()
color = pmma.ColorConverter()
clock = pygame.time.Clock()

start = time.perf_counter()
now_time = 0

pmma.set_in_game_loop(True)

surface = pygame.Surface((1920, 1080))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    surface.blit(display, (0, 0))
    display.fill([0, 0, 0])
    surface.set_alpha(254)
    display.blit(surface, (0, 0))

    points = []
    for x in range(1920):
        points.append((x, noise.generate_2D_perlin_noise(x/1920, now_time/5, new_range=[0, 1080])))
    pygame.draw.lines(display, color.generate_color_from_perlin_noise(now_time/5), False, points, 1)

    pmma.compute()

    pygame.display.update()
    clock.tick(60)
    now_time = time.perf_counter() - start