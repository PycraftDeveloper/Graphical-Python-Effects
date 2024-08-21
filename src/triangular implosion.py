import pmma

import math
import numpy as np

import time

import pygame

pmma.init(log_information=True)

display = pygame.display.set_mode((0, 0), flags=pygame.FULLSCREEN)
#display = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

advmath = pmma.Math()

noise = pmma.Perlin()

color_component = pmma.Color()

class Triangle:
    def __init__(self):
        self.center = display.get_width() / 2, display.get_height() / 2
        self.radius = min(display.get_width(), display.get_height()) / 2
        #self.radius = advmath.pythag(display.get_size())

    def draw(self, theta):
        angles = np.array([0, 2*np.pi/3, 4*np.pi/3]) # triangle

        # Calculate the coordinates of the vertices
        vertices = []
        for angle in angles:
            x = self.center[0] + self.radius * np.cos(angle)
            y = self.center[1] + self.radius * np.sin(angle)
            vertices.append([x, y])
        # Draw the equilateral triangle

        vertices = np.array(vertices)

        # Rotation matrix
        rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                                    [np.sin(theta), np.cos(theta)]])
        # Subtract the center, apply rotation, and then add the center back
        rotated_vertices = np.dot(vertices - self.center, rotation_matrix) + self.center

        color = color_component.generate_color(time.perf_counter())

        pygame.draw.polygon(
            display,
            (color),
            rotated_vertices,
            width=7)

        for vertex in rotated_vertices:
            pygame.draw.circle(display, (0, 0, 0), vertex, 50)

triangle_shape = Triangle()
K = 75 #50

TAU = 2 * math.pi

def scaler():
    surface =  pygame.transform.smoothscale(display, (display.get_width()-K, display.get_height()-K))
    display.fill([0, 0, 0])
    display.blit(surface, ((display.get_width() - surface.get_width())/2, (display.get_height() - surface.get_height())/2))

angle = 0
scale = 15 # 30
while pmma.Backpack.running:
    scaler()
    #display.fill([0, 0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pmma.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pmma.quit()
                quit()

    triangle_shape.draw(angle)
    angle += noise.generate_1D_perlin_noise(time.perf_counter(), new_range=[-1/scale, 1/scale])

    clock.tick(75)
    pygame.display.flip()

    pmma.compute()