import pmma
import random
import time
import pygame
from PIL import Image, ImageFilter

def display_to_string(surface, mode:str="RGBA") -> bytes:
    surface_image = pygame.image.tostring(
            surface,
            mode)

    return surface_image

def pygame_surface_to_pil_image(surface, mode:str="RGBA"):
    return Image.frombytes(
        mode,
        surface.get_size(),
        display_to_string(surface, mode=mode),
        "raw")

def pil_image_to_pygame_surface(image, alpha=True):
    surface = pygame.image.fromstring(
        image.tobytes(),
        image.size,
        image.mode)
    if alpha:
        surface.convert_alpha()
    if alpha is False:
        surface.convert()
    return surface

K = -20
HALF_K = K/2

def scaler(surface):
    tempsurf = pygame.Surface((canvas.get_width(), canvas.get_height()))
    surface =  pygame.transform.smoothscale(surface, (canvas.get_width()+K, canvas.get_height()+K))
    tempsurf.blit(surface, ((canvas.get_width()-surface.get_width())/2, (canvas.get_height()-surface.get_height())/2))
    return tempsurf

canvas = pmma.Display()
canvas.create(1280, 720)

events = pmma.Events()

registry = pmma.Registry()

now_time = 0
start = time.perf_counter()

class Point:
    def __init__(self):
        self.noise_x = pmma.Perlin(random.randint(0, 999999))
        self.noise_y = pmma.Perlin(random.randint(0, 999999))

        self.noise_s = pmma.Perlin(random.randint(0, 999999))

        self.noise_color = pmma.Perlin(random.randint(0, 999999))

    def compute(self):
        self.x = self.noise_x.generate_2D_perlin_noise(now_time/5, 0, [0, canvas.get_width()])
        self.y = self.noise_y.generate_2D_perlin_noise(now_time/5, 0, [0, canvas.get_height()])

        self.s = self.noise_s.generate_2D_perlin_noise(now_time/100, 0, [1, 10])

        self.r = self.noise_color.generate_2D_perlin_noise(now_time, 0, [0, 255])
        self.g = self.noise_color.generate_2D_perlin_noise(0, now_time, [0, 255])
        self.b = self.noise_color.generate_2D_perlin_noise(now_time, now_time, [0, 255])

    def render(self):
        pygame.draw.circle(surface, (self.r, self.g, self.b), (self.x, self.y), self.s)
        pygame.draw.circle(surface, (0, 0, 0), (self.x, self.y), self.s-2)

points = []
N = 20
for i in range(20):
    points.append(Point())

surface = pygame.Surface((canvas.get_width(), canvas.get_height()))

while registry.running:
    canvas.clear(0, 0, 0)

    events.handle(canvas)

    for point in points:
        point.compute()
        point.render()

    surface = scaler(surface)
    canvas.blit(surface, (0, 0))

    canvas.refresh()
    now_time = time.perf_counter()-start