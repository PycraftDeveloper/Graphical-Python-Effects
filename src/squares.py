<<<<<<< Updated upstream

import random
import time
import pmma
import pygame
import math

canvas = pmma.Display()
canvas.create(1280, 720)
events = pmma.Events()

registry = pmma.Registry

color_perlin = pmma.Perlin(random.randint(0, 9999))
rotation_perlin = pmma.Perlin(random.randint(0, 9999))

SWITCH = False

def draw_rectangle(x, y, width, height, color, rotation=0): # https://stackoverflow.com/a/73855696
    """Draw a rectangle, centered at x, y.
    All credit to Tim Swast for this `function that helped make this possible!

    Arguments:
      x (int/float):
        The x coordinate of the center of the shape.
      y (int/float):
        The y coordinate of the center of the shape.
      width (int/float):
        The width of the rectangle.
      height (int/float):
        The height of the rectangle.
      color (str):
        Name of the fill color, in HTML format.
    """
    points = []

    # The distance from the center of the rectangle to
    # one of the corners is the same for each corner.
    radius = math.sqrt((height / 2)**2 + (width / 2)**2)

    # Get the angle to one of the corners with respect
    # to the x-axis.
    angle = math.atan2(height / 2, width / 2)

    # Transform that angle to reach each corner of the rectangle.
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]

    # Convert rotation from degrees to radians.
    rot_radians = (math.pi / 180) * rotation

    # Calculate the coordinates of each point.
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset, y + y_offset))

    pygame.draw.polygon(canvas.surface, color, points)

class Square:
    def __init__(self, n):
        self.n = n/10
        self.size = n
        self.iter = n

    def render(self, now_time):
        color = [
            color_perlin.generate_2D_perlin_noise((now_time+self.n)/75, 0, [0, 255]),
            color_perlin.generate_2D_perlin_noise(0, (now_time+self.n)/75, [0, 255]),
            color_perlin.generate_2D_perlin_noise(-(now_time+self.n)/75, 0, [0, 255])
        ]
        draw_rectangle(*center, self.size, self.size, color, rotation=self.n)

        if SWITCH:
          self.n = rotation_perlin.generate_2D_perlin_noise(-(now_time+self.iter)/1000, 0, [0, 360]) # 500
        else:
          self.n += 0.5

squares = []
diag = int(math.sqrt(canvas.get_width()**2 + canvas.get_width()**2))
for i in range(0, diag, 8):
    squares.append(Square(diag-i))

start = time.perf_counter()
now_time = 0
while registry.running:
    #k = time.perf_counter()
    center = (canvas.get_width()/2, canvas.get_height()/2)

    canvas.clear(pygame.transform.average_color(canvas.surface))

    events.handle(canvas)

    for square in squares:
        square.render(now_time)

    canvas.refresh(refresh_rate=15)
    now_time = time.perf_counter() - start
    #s = time.perf_counter()
=======

import random
import time
import pmma
import pygame
import math

canvas = pmma.Display()
canvas.create(1280, 720)
events = pmma.Events()

registry = pmma.Registry

color_perlin = pmma.Perlin(random.randint(0, 9999))
rotation_perlin = pmma.Perlin(random.randint(0, 9999))

SWITCH = False

def draw_rectangle(x, y, width, height, color, rotation=0): # https://stackoverflow.com/a/73855696
    """Draw a rectangle, centered at x, y.
    All credit to Tim Swast for this function that helped make this possible!

    Arguments:
      x (int/float):
        The x coordinate of the center of the shape.
      y (int/float):
        The y coordinate of the center of the shape.
      width (int/float):
        The width of the rectangle.
      height (int/float):
        The height of the rectangle.
      color (str):
        Name of the fill color, in HTML format.
    """
    points = []

    # The distance from the center of the rectangle to
    # one of the corners is the same for each corner.
    radius = math.sqrt((height / 2)**2 + (width / 2)**2)

    # Get the angle to one of the corners with respect
    # to the x-axis.
    angle = math.atan2(height / 2, width / 2)

    # Transform that angle to reach each corner of the rectangle.
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]

    # Convert rotation from degrees to radians.
    rot_radians = (math.pi / 180) * rotation

    # Calculate the coordinates of each point.
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset, y + y_offset))

    pygame.draw.polygon(canvas.surface, color, points)

class Square:
    def __init__(self, n):
        self.n = n/10
        self.size = n
        self.iter = n

    def render(self, now_time):
        color = [
            color_perlin.generate_2D_perlin_noise((now_time+self.n)/75, 0, [0, 255]),
            color_perlin.generate_2D_perlin_noise(0, (now_time+self.n)/75, [0, 255]),
            color_perlin.generate_2D_perlin_noise(-(now_time+self.n)/75, 0, [0, 255])
        ]
        draw_rectangle(*center, self.size, self.size, color, rotation=self.n)

        if SWITCH:
          self.n = rotation_perlin.generate_2D_perlin_noise(-(now_time+self.iter)/1000, 0, [0, 360]) # 500
        else:
          self.n += 0.5

squares = []
diag = int(math.sqrt(canvas.get_width()**2 + canvas.get_width()**2))
for i in range(0, diag, 8):
    squares.append(Square(diag-i))

start = time.perf_counter()
now_time = 0
while registry.running:
    #k = time.perf_counter()
    center = (canvas.get_width()/2, canvas.get_height()/2)

    canvas.clear(pygame.transform.average_color(canvas.surface))

    events.handle(canvas)

    for square in squares:
        square.render(now_time)

    canvas.refresh(refresh_rate=15)
    now_time = time.perf_counter() - start
    #s = time.perf_counter()
>>>>>>> Stashed changes
