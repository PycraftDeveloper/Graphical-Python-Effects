import pygame
import math
import time
import pmma

def create_gradient_surface(length, width, start_color, end_color):
    """Creates a horizontal gradient surface."""
    surface = pygame.Surface((length, width), pygame.SRCALPHA)
    for x in range(length):
        t = x / length
        color = (
            int(start_color[0] * (1 - t) + end_color[0] * t),
            int(start_color[1] * (1 - t) + end_color[1] * t),
            int(start_color[2] * (1 - t) + end_color[2] * t),
            255
        )
        pygame.draw.line(surface, color, (x, 0), (x, width))
    return surface

def blit_rotated_gradient(surface, start_pos, end_pos, start_color, end_color, width):
    """Blit a rotated gradient onto the screen between two points."""
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    length = int((dx ** 2 + dy ** 2) ** 0.5)

    gradient = create_gradient_surface(length, width, start_color, end_color)

    angle = -pygame.math.Vector2(dx, dy).angle_to((1, 0))  # Find the angle
    rotated_gradient = pygame.transform.rotate(gradient, angle)

    rect = rotated_gradient.get_rect(center=((start_pos[0] + end_pos[0]) // 2,
                                             (start_pos[1] + end_pos[1]) // 2))

    surface.blit(rotated_gradient, rect.topleft)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

inner_color = pmma.ColorConverter()
outer_color = pmma.ColorConverter()
radius = pmma.Perlin()

now_time = 0
start = time.perf_counter()
running = True
while running:
    rx = 1920 // 2 + int(math.sin(now_time) * radius.generate_1D_perlin_noise(now_time, new_range=[0, 1080 / 2]))
    ry = 1080 // 2 + int(math.cos(now_time) * radius.generate_1D_perlin_noise(now_time, new_range=[0, 1080 / 2]))

    blit_rotated_gradient(
        screen,
        (1920 // 2, 1080 // 2),
        (rx, ry),
        inner_color.generate_color_from_perlin_noise(format=pmma.Constants.RGB),
        outer_color.generate_color_from_perlin_noise(format=pmma.Constants.RGB),
        20)

    rx = 1920 // 2 + int(math.sin(now_time + math.pi) * radius.generate_1D_perlin_noise(now_time, new_range=[0, 1080 / 2]))
    ry = 1080 // 2 + int(math.cos(now_time + math.pi) * radius.generate_1D_perlin_noise(now_time, new_range=[0, 1080 / 2]))

    blit_rotated_gradient(
        screen,
        (1920 // 2, 1080 // 2),
        (rx, ry),
        inner_color.generate_color_from_perlin_noise(format=pmma.Constants.RGB),
        outer_color.generate_color_from_perlin_noise(format=pmma.Constants.RGB),
        20)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now_time = time.perf_counter() - start
    clock.tick(60)

pygame.quit()
