import pmma
import math
import pygame
import time

pygame.init()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

noise = pmma.Perlin()

class Circle:
    def __init__(self):
        self.radius = 0
        self.color = [0, 0, 0]
        self.position = [0, 0]

circles = []
for _ in range(7500): # 750
    circle = Circle()
    circle.radius = 10
    circle.color = [255, 255, 255]
    circle.position = [display.get_width() // 2, display.get_height() // 2]
    circles.append(circle)

offset = 0

def pythag(x, y):
    return math.sqrt((x*x)+(y*y))

ROOT_TWO = 2**0.5

clock = pygame.time.Clock()

now_time = 0

while True:
    s = time.perf_counter()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

    display.fill([0, 0, 0])

    for i in range(len(circles)):
        a = ((1/360)*i)
        pos = [(math.sin(i+offset)*a)/ (display.get_width() / display.get_height()), math.cos(i+offset)*a]
        distance = pythag(abs(pos[0]), abs(pos[1])) - circle.radius
        if distance < ROOT_TWO:
            size = noise.generate_1D_perlin_noise(-distance + now_time/2, new_range=[1, 50]) * (distance / ROOT_TWO)
            size = max(size, 1)
            circles[i].radius = size
            circles[i].position = [display.get_width() / 2 + pos[0] * display.get_width() / 2, display.get_height() / 2 + pos[1] * display.get_height() / 2]

    for i in range(len(circles)):
        pygame.draw.circle(display, circles[i].color, circles[i].position, circles[i].radius)

    pygame.display.flip()

    clock.tick(2000)
    e = time.perf_counter()
    now_time = e-s
    print(clock.get_fps())

pmma.quit()