import random
import sys
import pygame

pygame.init()

screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

c1 = [random.randint(0,255), False]
c2 = [random.randint(0,255), False]
c3 = [random.randint(0,255), False]

clock = pygame.time.Clock()

def breeze(value):
    if value[1] == False:
        value[0] -= 1 * random.random()
    else:
        value[0] += 1 * random.random()

    if value[0] >= 255:
        value[1] = False
        value[0] = 255
    elif value[0] <= 0:
        value[1] = True
        value[0] = 0

    return value

while True:
    screen.fill([c1[0], c2[0], c3[0]])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    c1 = breeze(c1)
    c2 = breeze(c2)
    c3 = breeze(c3)

    pygame.display.flip()
    clock.tick(60)
