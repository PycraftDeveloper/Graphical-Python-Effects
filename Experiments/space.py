import pmma
import random
import pygame

canvas = pmma.Display()
canvas.create(1280, 720)

draw = pmma.Draw(canvas)

events = pmma.Events()
registry = pmma.Registry()

display_rect = pygame.Rect(0, 0, canvas.get_width(), canvas.get_height())

class Object:
    def __init__(self, radius=2):
        self.x = random.randint(0, canvas.get_width())
        self.y = random.randint(0, canvas.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.weight = random.randint(1, 100)
        self.x_vel = (random.random()*2)-1
        self.y_vel = (random.random()*2)-1
        self.radius = radius
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)
        self.pos = pygame.Vector2(self.x, self.y)

    def compute(self):
        self.x += self.x_vel
        self.y += self.y_vel

        if self.x < 0:
            self.x = random.randint(0, canvas.get_width())
            self.x_vel *= -1
        elif self.x > canvas.get_width():
            self.x = random.randint(0, canvas.get_width())
            self.x_vel *= -1

        if self.y < 0:
            self.y = random.randint(0, canvas.get_height())
            self.y_vel *= -1
        elif self.y > canvas.get_height():
            self.y = random.randint(0, canvas.get_height())
            self.y_vel *= -1

        self.pos = pygame.Vector2(self.x, self.y)

        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)

        minobj = [float("inf"), None]

        pos = pygame.Vector2(self.x, self.y)

        if display_rect.colliderect(self.rect):
            index = 0
            for object in objects:
                if object != self:
                    dist = pos.distance_to(object.pos)
                    if dist < self.radius:
                        del objects[index]
                        self.weight += object.weight + 100
                        self.radius += object.radius

                    if dist < minobj[0] and object.weight > self.weight:
                        minobj[0] = dist
                        minobj[1] = object

                index += 1

            if minobj[1] is not None:
                self.x_vel = -minobj[1].x_vel + 0.05*minobj[1].radius
                self.y_vel = -minobj[1].y_vel + 0.05*minobj[1].radius

    def render(self):
        if display_rect.colliderect(self.rect):
            if self.radius == 1:
                draw.pixel(self.color, (self.x, self.y))
            else:
                draw.circle(self.color, (self.x, self.y), self.radius)

objects = []
for i in range(300):
    objects.append(Object())

while registry.running:
    canvas.clear(0, 0, 0)

    events.handle(canvas)

    for object in objects:
        object.compute()
        object.render()

    canvas.refresh()