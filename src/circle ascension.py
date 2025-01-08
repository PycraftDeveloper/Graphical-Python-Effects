import pygame
import pmma
import random

pygame.init()
pmma.init()

now_time = 0
class Circle:
    def __init__(self, x, y):
        self.position = [x, 150+y]
        self.inner_radius = pmma.Perlin()
        self.outer_radius_delta = random.randint(10, 50)
        self.inner_color = pmma.ColorConverter()
        self.outer_color = pmma.ColorConverter()

    def render(self):
        inner_color = self.inner_color.generate_color_from_perlin_noise(now_time)
        outer_color = self.outer_color.generate_color_from_perlin_noise(now_time)
        inner_radius = self.inner_radius.generate_1D_perlin_noise(now_time*2, new_range=[0, 100])
        pygame.draw.circle(screen, inner_color, self.position, inner_radius)
        pygame.draw.circle(screen, outer_color, self.position, inner_radius+self.outer_radius_delta, 2)

screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

circles = []
x = 0
N = 20
for i in range(20):
    circles.append(Circle(x, random.randint(0, 1080-150)))
    x += int(1920/N)

surface = pygame.Surface((1920, 1080))
while True:
    surface.blit(screen, (0, 0))
    screen.fill([0, 0, 0])
    screen.blit(surface, (0, 5))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    for circle in circles:
        circle.render()

    pygame.display.update()
    now_time = pmma.get_application_run_time() / 5