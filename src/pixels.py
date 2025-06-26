#type: ignore

import pygame, pmma, time, numpy, random

pygame.init()

d = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
c = pygame.time.Clock()

SIZE = 60

n = pmma.PerlinNoise()

def mix(value1, value2, mx):
    return value1 * mx + value2 * (1 - mx)

class Pix:
    def __init__(self, x, y):
        self.pos = x, y
        dist = (abs(x - d.get_width() / 2), abs(y - d.get_height() / 2))
        self.r = pmma.AdvancedMathematics.point_pythagorean_distance(dist)
        self.color = pmma.ColorConverter()
        self.d = random.random()

    def render(self, t):
        s = n.noise_1d((self.r/200) - t) # 75
        self.color.generate_color_from_perlin_noise(self.d + time.perf_counter()/15)
        c = self.color.get_color_RGB(detect_format=False).astype(numpy.float32)
        s = pmma.AdvancedMathematics.ranger(s, [-1, 1], [0, 1])

        c **= 2
        max_c = max(c)
        c *= 255 / max_c

        size = ((SIZE / 2) + (SIZE * s * 2)) - 4
        pygame.draw.rect(d, c * s, (self.pos[0]-size/2, self.pos[1] - size/2, size/2, size/2), border_radius=int(size / 6))

pixels = []
for x in range(0, d.get_width(), SIZE):
    for y in range(0, d.get_height(), SIZE):
        pixels.append(Pix(x + (SIZE / 4) * 3, y + (SIZE / 4) * 3))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    d.fill([0, 0, 0])

    for pixel in pixels:
        pixel.render(time.perf_counter())

    pygame.display.update()
    c.tick(60)