import pygame
import pmma
import random
import math
import time

pygame.init()
pmma.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

GRAVITY = 0.5  # Acceleration due to gravity
FRICTION = 0.9  # Energy retention on wall bounces
EXPLOSION_SPEED = 15  # Speed of explosion

class BouncyBall:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = 10
        self.vx = math.cos(angle) * EXPLOSION_SPEED  # Velocity in x direction
        self.vy = math.sin(angle) * EXPLOSION_SPEED  # Velocity in y direction
        color = pmma.ColorConverter()
        self.color = color.generate_color_from_perlin_noise()
        self.start_time = time.perf_counter()

    def render(self):
        pygame.draw.circle(display, self.color, (int(self.x), int(self.y)), self.radius)

    def compute(self, balls):
        # Apply gravity
        self.vy += GRAVITY

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Wall collisions
        if self.x - self.radius < 0:  # Left wall
            self.x = self.radius
            self.vx = -self.vx * FRICTION
        elif self.x + self.radius > display.get_width():  # Right wall
            self.x = display.get_width() - self.radius
            self.vx = -self.vx * FRICTION

        if self.y - self.radius < 0:  # Ceiling
            self.y = self.radius
            self.vy = -self.vy * FRICTION
        elif self.y + self.radius > display.get_height():  # Floor
            self.y = display.get_height() - self.radius
            self.vy = -self.vy * FRICTION

        if (time.perf_counter() - self.start_time) < 1:
            return False
        # Check collisions with other balls
        for other in balls:
            if other is not self:
                self.check_collision(other)

        if abs(self.vy) < 0.237 and int(self.y) == display.get_height() - self.radius:
            return True
        return False

    def check_collision(self, other):
        # Vector between ball centers
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)

        # Check if balls are overlapping
        if distance < self.radius + other.radius:
            # Resolve collision
            angle = math.atan2(dy, dx)

            # Velocity components along the collision axis
            self_vx = self.vx * math.cos(angle) + self.vy * math.sin(angle)
            other_vx = other.vx * math.cos(angle) + other.vy * math.sin(angle)

            # Exchange velocities
            self.vx, other.vx = (
                other_vx * math.cos(angle) - self_vx * math.sin(angle),
                self_vx * math.cos(angle) - other_vx * math.sin(angle),
            )

            # Resolve overlap
            overlap = (self.radius + other.radius - distance) / 2
            self.x += overlap * math.cos(angle)
            self.y += overlap * math.sin(angle)
            other.x -= overlap * math.cos(angle)
            other.y -= overlap * math.sin(angle)


def create_explosion(center_x, center_y, num_balls):
    """Create balls exploding outward from the center."""
    balls = []
    for i in range(num_balls):
        angle = i * (2 * math.pi / num_balls)  # Evenly spaced angles
        balls.append(BouncyBall(center_x, center_y, angle))
    return balls


# Initialize explosion
number_of_balls = random.randint(10, 120)
balls = create_explosion(display.get_width() / 2, display.get_height() / 2, number_of_balls)

surface = pygame.Surface((display.get_width(), display.get_height()))
# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    surface.blit(display, (0, 0))
    display.fill([0, 0, 0])  # Clear screen
    surface.set_alpha(200)
    display.blit(surface, (0, 0))

    index = 0
    while index < len(balls):
        ball = balls[index]
        if ball.compute(balls):
            balls.remove(ball)
        else:
            ball.render()
        index += 1

    if len(balls) == 0:
        number_of_balls = random.randint(10, 120)
        balls = create_explosion(display.get_width() / 2, display.get_height() / 2, number_of_balls)

    pygame.display.flip()
    clock.tick(60)