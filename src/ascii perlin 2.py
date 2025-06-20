import pmma, time, os
import pygame

pygame.init()

c = pygame.time.Clock()

noise = pmma.PerlinNoise(0)

# spa, dash, star, hash, amp, at
# -*#&@

y = 0
while True:
    size = os.get_terminal_size().columns

    for x in range(size):
        value = noise.noise_2d(x/100, y/100)

        if value < -0.67:
            print(' ', end='')
        elif value < -0.33:
            print('-', end='')
        elif value < 0:
            print('*', end='')
        elif value < 0.22:
            print('#', end='')
        elif value < 0.67:
            print('&', end='')
        else:
            print('@', end='')

    c.tick(30)
    y += 1