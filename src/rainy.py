import pygame, random
import pygame.gfxdraw

pygame.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

class Point:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(0, 1080)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def draw(self):
        pygame.gfxdraw.pixel(Surface, self.x, int(self.y), self.color)

    def compute(self):
        self.y += 1-(1/1920)*self.y

        if self.y > display.get_height():
            self.y = 0

points = []
NPOINTS = 1
for i in range(NPOINTS):
    for x in range(display.get_width()):
        points.append(Point(x))

while True:
    window_size = display.get_width(), display.get_height()

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

    for point in points:
        point.draw()
        point.compute()

    Surface2.set_alpha(1) # 10

    display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    pygame.display.flip()