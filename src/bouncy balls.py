import random

import pmma

import time

import pygame

import traceback

display = pmma.Display()
try:
    display.create(1280, 720)
except Exception:
    print(traceback.format_exc())
#display.create(1280, 720)

events = pmma.Events()

registry = pmma.Registry()

math = pmma.Math()

class Ball:
    def __init__(self):
        self.x = random.randint(0, display.get_width())
        self.y = random.randint(0, display.get_height())
        self.dir_x = (random.random()*2)-1
        self.dir_y = (random.random()*2)-1
        self.seed = pmma.Perlin()
        self.mass = self.seed.generate_2D_perlin_noise(0, 0, new_range=[0, 20])
        self.mag_x = random.random()*5
        self.mag_y = random.random()*5
        self.last_collision_time = time.perf_counter()
        self.color = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]

    def compute(self, balls, now_time):
        self.mass = self.seed.generate_2D_perlin_noise(now_time/100, 0, new_range=[0, 20])
        self.x += self.dir_x * self.mag_x
        self.y += self.dir_y * self.mag_y

        if self.x > display.get_width()-self.mass:
            self.x = display.get_width()-self.mass
            self.dir_x *= -1
            pygame.draw.circle(Surface, [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)], (self.x, self.y), self.mass*2, width=1)
        elif self.x < self.mass:
            self.x = self.mass
            self.dir_x *= -1
            pygame.draw.circle(Surface, [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)], (self.x, self.y), self.mass*2, width=1)

        if self.y > display.get_height()-self.mass:
            self.y = display.get_height()-self.mass
            self.dir_y *= -1
            pygame.draw.circle(Surface, [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)], (self.x, self.y), self.mass*2, width=1)
        elif self.y < self.mass:
            self.y = self.mass
            self.dir_y *= -1
            pygame.draw.circle(Surface, [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)], (self.x, self.y), self.mass*2, width=1)

        if time.perf_counter()-self.last_collision_time > 1/15:
            for ball in balls:
                if ball is self:
                    continue
                if abs(self.x-ball.x) < self.mass+ball.mass and abs(self.y-ball.y) < self.mass+ball.mass:
                    #self.x += (self.x-ball.x)/2
                    #self.y += (self.y-ball.y)/2
                    self.dir_x *= -1
                    self.dir_y *= -1
                    ball.dir_x *= -1
                    ball.dir_y *= -1
                    self.last_collision_time = time.perf_counter()
                    ball.last_collision_time = time.perf_counter()
                    self.color = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]
                    ball.color = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]
                    pygame.draw.circle(Surface, [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)], (self.x, self.y), self.mass*2, width=1)
                    pygame.draw.circle(Surface, [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)], (ball.x, ball.y), ball.mass*2, width=1)


    def render(self):
        pygame.draw.circle(Surface, self.color, (self.x, self.y), self.mass)

balls = []
n_balls = 50
for i in range(n_balls):
    balls.append(Ball())

start = time.perf_counter()
now_time = 0
while registry.running:
    window_x, window_y = display.get_size()
    window_size = (window_x, window_y)

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))

    events.handle()

    for ball in balls:
        ball.compute(balls, now_time)
        ball.render()

    Surface2.set_alpha(5) # 10

    display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    pmma.compute()

    display.refresh()

    now_time = time.perf_counter() - start