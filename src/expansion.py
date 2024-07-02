import pygame
import sys
import time

import pmma

noise = pmma.Perlin()
r_noise = pmma.Perlin()
g_noise = pmma.Perlin()
b_noise = pmma.Perlin()

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
screen.set_colorkey((0, 0, 0))
pygame.display.set_caption("Expand from Center")

# Variables for the expansion
expansion_factor = 0.0  # Start with 0 (no scale)
max_factor = 1.0        # Full size at factor 1.0
growth_rate = 0.01      # How fast it grows each frame

# Clock to control the frame rate
clock = pygame.time.Clock()

running = True
start = time.perf_counter()
now_time = 0
while running:
    # Load or create the surface to expand (e.g., an image)

    pygame.draw.circle(
        screen,
        (
            r_noise.generate_1D_perlin_noise(now_time/10, range=[0, 255]),
            g_noise.generate_1D_perlin_noise(now_time/10, range=[0, 255]),
            b_noise.generate_1D_perlin_noise(now_time/10, range=[0, 255])),
        (screen_width // 2, noise.generate_1D_perlin_noise(now_time/5, range=[0, screen.get_height()])), 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Increase the expansion factor
    expansion_factor += growth_rate

    # Calculate new size

    # Resize the surface
    surface = pygame.transform.smoothscale(screen, (screen.get_width()+2, screen.get_height()+2))

    # Calculate the position to center the surface on the screen
    pos_x = (screen_width - surface.get_width()) // 2
    pos_y = (screen_height - surface.get_height()) // 2

    # Blit the scaled surface onto the screen
    screen.blit(surface, (pos_x, pos_y))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 60 FPS
    clock.tick(60)
    now_time = time.perf_counter() - start

# Quit Pygame
pygame.quit()
sys.exit()
