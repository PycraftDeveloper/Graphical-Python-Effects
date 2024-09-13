import pygame
import math
import pmma
import time

# Initialize Pygame
pygame.init()
pmma.init()

w_noise = pmma.Perlin()
h_noise = pmma.Perlin()

color = pmma.ColorConverter()

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Rotating Ellipse')

# Define colors

# Ellipse parameters
ellipse_width, ellipse_height = 200, 100
angle = 0  # Initial angle of rotation

# Function to draw a rotating ellipse
def draw_rotating_ellipse(surface, center, width, height, angle, color):
    # Create a separate surface to draw the ellipse
    ellipse_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    ellipse_surface.fill((0, 0, 0, 0))  # Make it transparent

    # Draw the ellipse on the surface
    pygame.draw.ellipse(ellipse_surface, color, (0, 0, width, height), 3)

    # Rotate the ellipse
    rotated_ellipse = pygame.transform.rotate(ellipse_surface, angle)

    # Get the new rectangle of the rotated ellipse to keep it centered
    rotated_rect = rotated_ellipse.get_rect(center=center)

    # Blit the rotated ellipse onto the main surface
    surface.blit(rotated_ellipse, rotated_rect.topleft)

# Main loop
running = True
clock = pygame.time.Clock()
start = time.perf_counter()
now_time = 0
surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
surface.set_alpha(253)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    surface.blit(screen, (0, 0))
    screen.fill([0, 0, 0])
    screen.blit(surface, (0, 0))

    # Calculate the center of the screen
    center = (screen.get_width() // 2, screen.get_height() // 2)

    # Increase the rotation angle
    angle += 1  # Increase angle for rotation (can adjust speed)

    # Draw the rotating ellipse
    draw_rotating_ellipse(
        screen,
        center,
        w_noise.generate_1D_perlin_noise(now_time/20, new_range=[100, screen.get_height()]),
        h_noise.generate_1D_perlin_noise(now_time/20, new_range=[100, screen.get_height()]),
        angle,
        color.generate_color(now_time/25))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)
    now_time = time.perf_counter() - start
    pmma.compute()

pygame.quit()
