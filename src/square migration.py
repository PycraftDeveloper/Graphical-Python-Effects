import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQUARE_SIZE = 7
SPACING = 3
TOTAL_SQUARES = (SCREEN_WIDTH) // (SQUARE_SIZE + SPACING)
FPS = 60
MOVE_DURATION = 3000  # Time in milliseconds for each movement
MAX_Y_VARIATION = 50  # Maximum random Y-axis gain/loss

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Square class
class Square:
    def __init__(self, x, y, color):
        self.initial_pos = (x, y)
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.color = color
        self.start_time = pygame.time.get_ticks()
        self.move_duration = MOVE_DURATION

        # Intermediate Y target and velocity for vertical movement
        self.intermediate_y = y
        self.velocity_x = 0
        self.velocity_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, SQUARE_SIZE, SQUARE_SIZE))

    def move(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= self.move_duration:
            self.x = self.target_x
            self.y = self.target_y
        else:
            # Progress ratio (from 0 to 1)
            progress = elapsed_time / self.move_duration

            # Calculate non-linear motion based on progress
            self.x = self.lerp(self.x, self.target_x, progress)
            self.y = self.vertical_movement(progress)

    def set_new_target(self, new_x, new_y):
        self.target_x = new_x
        self.target_y = SCREEN_HEIGHT // 2 - SQUARE_SIZE // 2  # Ensure target is always on the center line
        self.start_time = pygame.time.get_ticks()

        # Set intermediate Y for random variation
        self.intermediate_y = self.y + random.randint(-MAX_Y_VARIATION, MAX_Y_VARIATION)

        # Set velocities based on random speed factor for vertical movements
        self.velocity_x = (self.target_x - self.x) / self.move_duration
        self.velocity_y = (self.intermediate_y - self.y) / (self.move_duration / 2)  # Faster to Y-offset

    def lerp(self, start, end, progress):
        return start + (end - start) * progress

    def vertical_movement(self, progress):
        # First half: Move towards random Y offset, then return to center line
        if progress < 0.5:
            return self.lerp(self.y, self.intermediate_y, progress * 2)
        else:
            return self.lerp(self.intermediate_y, self.target_y, (progress - 0.5) * 2)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Square Movement with Dynamic Vertical Motion")

# Create squares
squares = []
for i in range(TOTAL_SQUARES):
    x = i * (SQUARE_SIZE + SPACING)
    y = SCREEN_HEIGHT // 2 - SQUARE_SIZE // 2
    square = Square(x, y, RED)
    squares.append(square)

# Main loop
running = True
clock = pygame.time.Clock()
last_swap_time = pygame.time.get_ticks()

while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Time-based target swapping
    current_time = pygame.time.get_ticks()
    if current_time - last_swap_time > MOVE_DURATION:
        # Swap target positions randomly
        positions = [(square.x, square.y) for square in squares]
        random.shuffle(positions)
        for i, square in enumerate(squares):
            new_x, new_y = positions[i]
            square.set_new_target(new_x, new_y)
        last_swap_time = current_time

    # Move squares and draw them
    for square in squares:
        square.move()
        square.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
