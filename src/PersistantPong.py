import random

import pmma

pmma.set_profile_result_path(r"H:\Downloads\New Text Document (2).txt")

pmma.init()#general_profile_application=True)

display = pmma.Display()
display.create()

events = pmma.Events()

general = pmma.General()

class Tile:
    def __init__(self, position):
        self.position = position

        self.square = pmma.Rectangle()
        self.square.set_center(position)
        self.square.set_size([60, 60])

        if position[0] < display.get_width() / 2:
            self.color = [255, 255, 255]
        else:
            self.color = [0, 0, 0]
        self.square.set_color(self.color)

    def Render(self):
        self.square.render()

    def set_color(self, color):
        self.color = color
        self.square.set_color(color)

    def get_bounds(self):
        x, y = self.position
        half = 12.5
        return (x - half, y - half, x + half, y + half)

    def collides_with(self, pos):
        x, y = pos
        left, top, right, bottom = self.get_bounds()
        return left - 25 <= x <= right + 25 and top - 25 <= y <= bottom + 25

class Ball:
    def __init__(self, position):
        self.position = position

        if self.position[0] < display.get_width() / 2:
            self.velocity = [15, (random.random() * 30) - 15]
            self.color = [0, 0, 0]
            self.opposite_color = [255, 255, 255]
        else:
            self.velocity = [-15, (random.random() * 30) - 15]
            self.color = [255, 255, 255]
            self.opposite_color = [0, 0, 0]

        self.circle = pmma.Circle()
        self.circle.set_center(position)
        self.circle.set_radius(25)
        self.circle.set_color(self.color)

    def Update(self):
        self.circle.render()

        next_pos = [self.position[0] + self.velocity[0], self.position[1] + self.velocity[1]]

        for tile in tiles:
            if tile.collides_with(next_pos) and tile.color == self.color:
                tile.set_color(self.opposite_color)
                self.velocity[0] *= -1  # Reverse direction on X-axis
                self.velocity[1] *= -1
                break  # Prevent multiple collisions per update

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        if self.position[0] - 25 < 0 or self.position[0] + 25 > display.get_width():
            self.velocity[0] *= -1
            self.velocity[1] = (random.random() * 20) - 10
            if (self.position[0] + 25) > display.get_width():
                self.position[0] = display.get_width() - 25
            else:
                self.position[0] = 25
        if self.position[1] - 25 < 0 or self.position[1] + 25 > display.get_height():
            self.velocity[1] *= -1
            if (self.position[1] + 25) > display.get_height():
                self.position[1] = display.get_height() - 25
            else:
                self.position[1] = 25

        self.circle.set_center(self.position)

tiles = []
for i in range(0, display.get_width(), 60):
    for j in range(0, display.get_height(), 60):
        tiles.append(Tile((i+30, j+30)))

balls = []
balls.append(Ball([display.get_width() - 25, display.get_height() / 2]))
balls.append(Ball([25, display.get_height() / 2]))

color = pmma.ColorConverter()

import time
time.sleep(10)

while pmma.get_application_running():
    display.clear()
    events.handle()

    for tile in tiles:
        tile.Render()

    for ball in balls:
        ball.Update()

    general.compute()
    display.refresh()

general.quit()
