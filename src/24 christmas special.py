import pygame
import numpy as np
import sys
import pmma

pmma.init()

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Randomized Gradient Snowflake")

# Colors
BLACK = (0, 0, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()

color_one = pmma.ColorConverter()
color_two = pmma.ColorConverter()
ang = pmma.Perlin()

def random_angle():
    """Generate a small random angle variation."""
    return ang.generate_1D_perlin_noise(new_range=[-np.pi / 6, np.pi / 6])

def interpolate_color(start_color, end_color, t):
    """Interpolate between two colors based on t (0 <= t <= 1)."""
    return [
        int(start_color[i] + (end_color[i] - start_color[i]) * t) for i in range(3)
    ]


def draw_gradient_line(surface, start_pos, end_pos, start_color, end_color):
    """Draw a line with a gradient between two colors."""
    steps = int(np.linalg.norm(np.array(end_pos) - np.array(start_pos)))
    for i in range(steps):
        t = i / steps
        color = interpolate_color(start_color, end_color, t)
        pos = (
            start_pos[0] + (end_pos[0] - start_pos[0]) * t,
            start_pos[1] + (end_pos[1] - start_pos[1]) * t,
        )
        pygame.draw.circle(surface, color, (int(pos[0]), int(pos[1])), 1)


def randomized_koch_snowflake(order, p1, p2, start_color, end_color):
    """Draw a Koch snowflake edge with randomization and gradient colors."""
    if order == 0:
        draw_gradient_line(screen, p1, p2, start_color, end_color)
        return

    # Divide the line into thirds
    p3 = p1 + (p2 - p1) / 3
    p5 = p1 + 2 * (p2 - p1) / 3

    # Compute the peak of the triangle with randomization
    angle = np.pi / 3 + random_angle()
    direction = p5 - p3
    p4 = p3 + np.array([
        direction[0] * np.cos(angle) - direction[1] * np.sin(angle),
        direction[0] * np.sin(angle) + direction[1] * np.cos(angle)
    ])

    # Split colors for the gradient
    color1 = interpolate_color(start_color, end_color, 1/3)
    color2 = interpolate_color(start_color, end_color, 2/3)

    # Recursively draw the segments
    randomized_koch_snowflake(order - 1, p1, p3, start_color, color1)
    randomized_koch_snowflake(order - 1, p3, p4, color1, color2)
    randomized_koch_snowflake(order - 1, p4, p5, color2, end_color)
    randomized_koch_snowflake(order - 1, p5, p2, end_color, end_color)


def draw_random_snowflake(order, center, size):
    """Draw a randomized Koch snowflake with gradient colors."""
    # Initial equilateral triangle
    angle = np.pi / 3
    p1 = center + np.array([-size / 2, size * np.sqrt(3) / 6])
    p2 = center + np.array([size / 2, size * np.sqrt(3) / 6])
    p3 = center + np.array([0, -size * np.sqrt(3) / 3])

    # Generate random gradient colors
    start_color = color_one.generate_color_from_perlin_noise(format=pmma.Constants.RGB)
    end_color = color_two.generate_color_from_perlin_noise(format=pmma.Constants.RGB)

    # Draw the edges with gradients
    randomized_koch_snowflake(order, p1, p2, start_color, end_color)
    randomized_koch_snowflake(order, p2, p3, start_color, end_color)
    randomized_koch_snowflake(order, p3, p1, start_color, end_color)


# Main loop
def main():
    order = 4  # Fixed recursion depth for performance
    size = 850
    center = np.array([WIDTH // 2, HEIGHT // 2])
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the screen
        screen.fill(BLACK)

        # Draw the randomized snowflake with gradient
        draw_random_snowflake(order, center, size)

        pmma.compute()

        # Update the display
        pygame.display.flip()

        # Control frame rate
        clock.tick(60)  # Run at 60 FPS


# Run the program
if __name__ == "__main__":
    main()
