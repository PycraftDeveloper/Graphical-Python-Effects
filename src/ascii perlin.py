import pmma, time, os
import pygame

pygame.init()

c = pygame.time.Clock()

noise = pmma.PerlinNoise()

while True:
    value = (1+noise.noise_1d(time.perf_counter())) * 0.5

    size = os.get_terminal_size().columns

    print('#'*int(value*size))

    c.tick(30)