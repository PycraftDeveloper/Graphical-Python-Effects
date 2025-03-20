import pygame
import math
import pmma

pygame.init()
pmma.init()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

clock = pygame.time.Clock()

class Line:
    def __init__(self, x, y, dx, dy, seed):
        self.start = (x, y)
        self.dir = (dx, dy)
        self.points = [self.start] * 2
        self.color = pmma.ColorConverter()
        self.color.set_red_seed(seed)
        self.color.set_green_seed(seed+10)
        self.color.set_blue_seed(seed+20)
        self.dx_offset = pmma.Perlin(seed)
        self.dy_offset = pmma.Perlin(seed+10)
        self.new = True

    def update(self):
        pygame.draw.lines(display, self.color.generate_color_from_perlin_noise(pmma.get_application_run_time()/500, format=pmma.Constants.RGB, color_range=[0, 255]), False, self.points, width=3)
        if self.points[-1][0] < 0 or self.points[-1][0] > display.get_width() or self.points[-1][1] < 0 or self.points[-1][1] > display.get_height():
            self.new = False
            return

        self.points.append((
            self.points[-1][0] + self.dir[0] * self.dx_offset.generate_1D_perlin_noise(self.dir[0]*len(self.points)/100, new_range=[0, 3]),
            self.points[-1][1] + self.dir[1] * self.dy_offset.generate_1D_perlin_noise(self.dir[1]*len(self.points)/100, new_range=[0, 3])))

lines = []
n = 0

def generate_lines(radius=50, num_points=200):
    global lines, n
    screen_width, screen_height = display.get_size()
    cx, cy = screen_width // 2, screen_height // 2
    new = [
        Line(cx + int(radius * math.cos(2 * math.pi * i / num_points)),
              cy + int(radius * math.sin(2 * math.pi * i / num_points)),
              math.cos(2 * math.pi * i / num_points),
              math.sin(2 * math.pi * i / num_points),
              n)
        for i in range(num_points)
    ]
    lines.extend(new)
    n += 1

generate_lines()

surface = pygame.Surface(display.get_size(), pygame.SRCALPHA)
alpha = 255
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    display.fill((0, 0, 0))
    if alpha >= 0 and alpha <= 255:
        surface.set_alpha(alpha)
    display.blit(surface, (0, 0))
    alpha -= 0.5

    new = True
    for line in lines:
        line.update()
        new &= not line.new

    if new:
        lines = []
        generate_lines()

    pmma.compute()
    pygame.display.update()

    if new:
        surface.blit(display, (0, 0))
        alpha = 255
    clock.tick(60)