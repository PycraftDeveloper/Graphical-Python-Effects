import pmma
import pygame

pmma.init()

point_one_noise = [pmma.Perlin(), pmma.Perlin()]
point_two_noise = [pmma.Perlin(), pmma.Perlin()]

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

color = pmma.ColorConverter()

clock = pygame.time.Clock()

surface = pygame.Surface((1920, 1080))

while pmma.get_application_running():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pmma.set_application_running(False)

    surface.blit(display, (0, 0))
    display.fill([0, 0, 0])
    surface.set_alpha(254)
    display.blit(surface, (0, 0))

    timer = int(pmma.get_application_run_time()*40)/40

    coordinate_one = [point_one_noise[0].generate_1D_perlin_noise(timer, new_range=[0, 1920]), point_one_noise[1].generate_1D_perlin_noise(timer, new_range=[0, 1080])]
    coordinate_two = [point_two_noise[0].generate_1D_perlin_noise(timer, new_range=[0, 1920]), point_two_noise[1].generate_1D_perlin_noise(timer, new_range=[0, 1080])]

    pygame.draw.line(display, color.generate_color_from_perlin_noise(), coordinate_one, coordinate_two, 10)

    pmma.compute()
    pygame.display.update()
    clock.tick(60)