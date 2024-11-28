import pmma
import random
import time
import pygame
import math

pmma.init()
pygame.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

class Ball:
    def __init__(self, x):
        self.x = x
        self.y = display.get_height() + 300
        self.radius = random.randint(1, 100)
        self.time = time.perf_counter()
        self.color_converter = pmma.ColorConverter()
        self.color = self.color_converter.generate_random_color()
        self.destroy = False
        self.size_change_time = 3
        self.distance_moved = 0
        self.do_once = False

    def collision(self, other_ball):
        # Distance between centers
        distance = math.sqrt((self.x - other_ball.x)**2 + (self.y - other_ball.y)**2)
        if distance <= self.radius + other_ball.radius:
            # Adjust positions slightly to avoid overlap
            overlap = self.radius + other_ball.radius - distance
            angle = math.atan2(other_ball.y - self.y, other_ball.x - self.x)
            self.x -= math.cos(angle) * overlap / 2
            self.y -= math.sin(angle) * overlap / 2
            other_ball.x += math.cos(angle) * overlap / 2
            other_ball.y += math.sin(angle) * overlap / 2

    def compute(self):
        self.y -= 3

        if self.y + self.radius <= 0:
            self.destroy = True

    def to_destroy(self):
        return self.destroy

    def render(self):
        if not self.destroy:
            pygame.draw.circle(display, self.color, (self.x, int(self.y)), self.radius)

balls = []
for i in range(150):
    balls.append(Ball(random.randint(0, display.get_width())))

while pmma.get_application_running():
    #display.fill(pygame.transform.average_color(display))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pmma.set_application_running(False)

    for ball in balls:
        ball.render()
        ball.compute()
        for other_ball in balls:
            if ball != other_ball:
                ball.collision(other_ball)
        if ball.to_destroy():
            balls.remove(ball)

    for i in range(0, 150-len(balls)):
        balls.append(Ball(random.randint(0, display.get_width())))

    pmma.compute()

    pygame.display.update()
    clock.tick(60)