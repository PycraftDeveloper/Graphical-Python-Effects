import math
import pygame
import pmma
import time

# Set up display
display = pygame.display.set_mode((1920, 1080), flags=pygame.FULLSCREEN)
clock = pygame.time.Clock()

timer = 0
circ_offset = pmma.PerlinNoise()

color_converter = pmma.ColorConverter()

def circle(timer, adjusted_radius):
    center_x, center_y = 1920 / 2, 1080 / 2
    circle_points = []

    for angle in range(360):
        rad = math.radians(angle)

        # Sample noise in a circular path to ensure smooth wrapping
        noise_x = math.cos(rad)
        noise_y = math.sin(rad)

        # Animate with timer
        noise_val = circ_offset.noise_3d(noise_x, noise_y, timer * 0.2)

        # Modulate the radius
        radius = adjusted_radius + noise_val * adjusted_radius

        x = center_x + math.cos(rad) * radius
        y = center_y + math.sin(rad) * radius
        circle_points.append((x, y))

    color_converter.generate_color_from_perlin_noise((timer / 2)+(adjusted_radius/100))

    pygame.draw.lines(
        display,
        color_converter.get_color_RGB(),
        True,
        circle_points,
        10)

start = time.perf_counter()

# Main loop
while True:
    display.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    end = time.perf_counter()
    timer = end - start

    for i in range(30): # 15
        circle(timer, 50 + i * 50)

    pygame.display.flip()
    clock.tick(60)
