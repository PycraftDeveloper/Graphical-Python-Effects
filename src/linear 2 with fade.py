import pmma
import time
import pygame

display = pmma.Display()
display.create(1920, 1080, fullscreen=True)

events = pmma.Events(display)

seed = pmma.Perlin()

start = time.perf_counter()
now_time = 0
while True:
    window_x, window_y = display.get_size()
    window_size = (window_x, window_y)

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))

    events.handle()

    center = display.get_center()

    color = [seed.generate_2D_perlin_noise(0, now_time/10, range=[0, 255]), seed.generate_2D_perlin_noise(0, -now_time/10, range=[0, 255]), seed.generate_2D_perlin_noise(now_time/10, 0, range=[0, 255])]

    line_points = []
    for x in range(center[0], 0, -1):
        y_displacement = seed.generate_2D_perlin_noise(x/100, now_time/10, range=[-center[1], center[1]])
        line_points.append((x, center[1]+y_displacement))
    pygame.draw.lines(Surface, color, False, line_points)


    line_points = []
    for x in range(center[0], display.get_width()):
        y_displacement = seed.generate_2D_perlin_noise(x/100, now_time/10, range=[-center[1], center[1]])
        line_points.append((x, center[1]+y_displacement))
    pygame.draw.lines(Surface, color, False, line_points)

    Surface2.set_alpha(1) # 10

    display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    display.refresh(60)
    now_time = time.perf_counter() - start