import pygame
import math
import pmma
import time
import random

# Initialize Pygame
pygame.init()
pmma.init()

# Screen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Circle settings
NUM_CIRCLES = 15
SPEED = 0.01  # Rotation speed
CIRCLE_RADIUS = 8  # Size of each circle
HEX_STEPS = 6  # Six steps for hexagonal motion
radius = 0

class Circle:
    def __init__(self, index, radius):
        """Initialize a circle at a fixed distance from the center."""
        self.angle = index * (2 * math.pi / NUM_CIRCLES)
        self.index = index  # Unique index for hexagonal stepping
        self.color = pmma.ColorConverter()
        self.radius = radius
        radius += CIRCLE_RADIUS
        self.angle = random.uniform(0, 2 * math.pi)  # Random starting angle

    def update(self):
        """Update position following a hexagonal path while keeping distance constant."""
        step_angle = (self.index % HEX_STEPS) * (math.pi / 3)  # Six-step hexagonal movement
        hex_offset = math.sin(self.angle * HEX_STEPS) * (self.radius * 0.1)  # Small hex variation

        x = screen.get_width() // 2 + (self.radius + hex_offset) * math.cos(self.angle + step_angle)
        y = screen.get_height() // 2 + (self.radius + hex_offset) * math.sin(self.angle + step_angle)

        pygame.draw.circle(screen, self.color.generate_color_from_perlin_noise(now_time / 7), (int(x), int(y)), CIRCLE_RADIUS)

        self.angle += SPEED  # Rotate around the center

circles = []
# Create circles
for i in range(NUM_CIRCLES):
    radius += CIRCLE_RADIUS * 4
    circles.append(Circle(i, radius))

running = True
now_time = 0
start = time.perf_counter()
while running:
    #screen.fill((0, 0, 0))  # Clear screen

    for circle in circles:
        circle.update()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60 * 2)  # 60 FPS
    now_time = time.perf_counter() - start
pygame.quit()
