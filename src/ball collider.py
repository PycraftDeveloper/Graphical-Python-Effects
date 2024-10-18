import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 1920, 1080
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
clock = pygame.time.Clock()

def pythagorean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class Ball:
    def __init__(self, x, y, mass, color):
        self.x = x
        self.y = y
        self.radius = mass
        self.color = color
        self.x_speed = random.randint(0, 20)
        self.y_speed = random.randint(0, 20)
        self.mass = mass

    def compute(self):
        self.x += self.x_speed
        self.y += self.y_speed

        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.x_speed = -self.x_speed
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.y_speed = -self.y_speed

        if self.x < 0:
            self.x = 0
        if self.x > width:
            self.x = width

        if self.y < 0:
            self.y = 0
        if self.y > height:
            self.y = height

    def collision(self, ball):
        # Calculate the distance between the two balls
        distance = pythagorean_distance(self.x, self.y, ball.x, ball.y)
        if distance < self.radius + ball.radius:
            # Calculate the angle of the collision
            angle = math.atan2(self.y - ball.y, self.x - ball.x)
            sin_angle = math.sin(angle)
            cos_angle = math.cos(angle)

            # Rotate the velocities so that the collision is head-on
            v1_x_rot = cos_angle * self.x_speed + sin_angle * self.y_speed
            v1_y_rot = cos_angle * self.y_speed - sin_angle * self.x_speed
            v2_x_rot = cos_angle * ball.x_speed + sin_angle * ball.y_speed
            v2_y_rot = cos_angle * ball.y_speed - sin_angle * ball.x_speed

            # Apply the 1D collision equations along the rotated axis
            v1_x_rot_new = (v1_x_rot * (self.mass - ball.mass) + 2 * ball.mass * v2_x_rot) / (self.mass + ball.mass)
            v2_x_rot_new = (v2_x_rot * (ball.mass - self.mass) + 2 * self.mass * v1_x_rot) / (self.mass + ball.mass)

            # Rotate the velocities back
            self.x_speed = cos_angle * v1_x_rot_new - sin_angle * v1_y_rot
            self.y_speed = sin_angle * v1_x_rot_new + cos_angle * v1_y_rot
            ball.x_speed = cos_angle * v2_x_rot_new - sin_angle * v2_y_rot
            ball.y_speed = sin_angle * v2_x_rot_new + cos_angle * v2_y_rot

            # Move the balls apart to prevent overlap
            overlap = 0.5 * (self.radius + ball.radius - distance)
            self.x += cos_angle * overlap
            self.y += sin_angle * overlap
            ball.x -= cos_angle * overlap
            ball.y -= sin_angle * overlap

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

balls = []
for _ in range(10):
    x = random.randint(100, width - 100)
    y = random.randint(100, height - 100)
    mass = random.randint(10, 50)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    balls.append(Ball(x, y, mass, color))

# Game loop
running = True
while running:
    screen.fill([255, 255, 255])

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for ball in balls:
        ball.compute()
        for other_ball in balls:
            if ball != other_ball:
                ball.collision(other_ball)
        ball.draw(screen)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
