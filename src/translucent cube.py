import pygame
import moderngl
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL, FULLSCREEN
from pyrr import Matrix44
import pmma
import time

pmma.init()


inner = pmma.ColorConverter()
outer = pmma.ColorConverter()

class Cube:
    def __init__(self, ctx, outer_size, inner_size, outer_color=(1.0, 0.0, 0.0, 1.0), inner_color=(0.0, 1.0, 0.0, 1.0), scale=1.0, outline=False):
        self.ctx = ctx
        self.outline = outline
        self.outer_size = outer_size
        self.inner_size = inner_size
        self.outer_color = outer_color
        self.inner_color = inner_color
        self.scale = scale  # The scale factor applied in the shader

        # Define the outer and inner cube vertices with their respective colors
        outer_vertices = np.array([
            # Outer cube vertices (x, y, z, r, g, b, a)
            -self.outer_size[0]/2, -self.outer_size[1]/2, -self.outer_size[2]/2, *outer_color,
            self.outer_size[0]/2, -self.outer_size[1]/2, -self.outer_size[2]/2, *outer_color,
            self.outer_size[0]/2, self.outer_size[1]/2, -self.outer_size[2]/2, *outer_color,
            -self.outer_size[0]/2, self.outer_size[1]/2, -self.outer_size[2]/2, *outer_color,
            -self.outer_size[0]/2, -self.outer_size[1]/2, self.outer_size[2]/2, *outer_color,
            self.outer_size[0]/2, -self.outer_size[1]/2, self.outer_size[2]/2, *outer_color,
            self.outer_size[0]/2, self.outer_size[1]/2, self.outer_size[2]/2, *outer_color,
            -self.outer_size[0]/2, self.outer_size[1]/2, self.outer_size[2]/2, *outer_color,
        ], dtype='f4')

        inner_vertices = np.array([
            # Inner cube vertices (x, y, z, r, g, b, a)
            -self.inner_size[0]/2, -self.inner_size[1]/2, -self.inner_size[2]/2, *inner_color,
            self.inner_size[0]/2, -self.inner_size[1]/2, -self.inner_size[2]/2, *inner_color,
            self.inner_size[0]/2, self.inner_size[1]/2, -self.inner_size[2]/2, *inner_color,
            -self.inner_size[0]/2, self.inner_size[1]/2, -self.inner_size[2]/2, *inner_color,
            -self.inner_size[0]/2, -self.inner_size[1]/2, self.inner_size[2]/2, *inner_color,
            self.inner_size[0]/2, -self.inner_size[1]/2, self.inner_size[2]/2, *inner_color,
            self.inner_size[0]/2, self.inner_size[1]/2, self.inner_size[2]/2, *inner_color,
            -self.inner_size[0]/2, self.inner_size[1]/2, self.inner_size[2]/2, *inner_color,
        ], dtype='f4')

        # Combine the vertices
        self.vertices = np.concatenate((outer_vertices, inner_vertices))

        # Define the indices for the cube faces (2 triangles per face)
        self.indices = np.array([
            # Outer cube
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            0, 1, 5, 0, 5, 4,
            1, 2, 6, 1, 6, 5,
            2, 3, 7, 2, 7, 6,
            3, 0, 4, 3, 4, 7,
            # Inner cube (similar but adjusted by width)
            8, 9, 10, 8, 10, 11,
            12, 13, 14, 12, 14, 15,
            8, 9, 13, 8, 13, 12,
            9, 10, 14, 9, 14, 13,
            10, 11, 15, 10, 15, 14,
            11, 8, 12, 11, 12, 15,
        ], dtype='i4')

        # Create buffers
        self.vbo = self.ctx.buffer(self.vertices)
        self.ibo = self.ctx.buffer(self.indices)

        self.program = self.ctx.program(
            vertex_shader="""
                #version 330
                uniform mat4 model;
                uniform float scale;  // The scaling factor
                in vec3 in_vert;
                in vec4 in_color;
                smooth out vec4 color;
                void main() {
                    gl_Position = model * vec4(in_vert * scale, 1.0);  // Apply scaling here
                    color = in_color;
                }
            """,
            fragment_shader="""
                #version 330
                smooth in vec4 color;
                out vec4 fragColor;
                void main() {
                    fragColor = color;
                }
            """
        )

        # Create the vertex array object (VAO)
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', 'in_color', index_buffer=self.ibo)

        # Initialize rotation matrix
        self.rotation_matrix = Matrix44.identity()

    def set_color(self, outer_color, inner_color):
        self.outer_color = outer_color
        self.inner_color = inner_color
        # Update the vertex buffer with new colors
        for i in range(8):  # Outer cube vertices
            start = i * 7
            self.vertices[start + 3:start + 7] = outer_color
        for i in range(8, 16):  # Inner cube vertices
            start = i * 7
            self.vertices[start + 3:start + 7] = inner_color
        self.vbo.write(self.vertices)

    def update_rotation(self, angle):
        rotation = Matrix44.from_eulers((angle, angle, 0), dtype='f4')
        self.rotation_matrix = rotation

    def render(self):
        self.program['model'].write(self.rotation_matrix)
        self.program['scale'].value = self.scale  # Pass the scale to the shader
        if self.outline:
            self.vao.render(moderngl.LINES)
        else:
            self.vao.render(moderngl.TRIANGLES)

def lerp_color(color1, color2, t):
    return tuple((1 - t) * c1 + t * c2 for c1, c2 in zip(color1, color2))

# Initialize Pygame and ModernGL
pygame.init()
screen = pygame.display.set_mode((0, 0), DOUBLEBUF | OPENGL | FULLSCREEN)
ctx = moderngl.create_context()

ctx.enable(moderngl.BLEND)
ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

# Define your outer and inner colors
outer_color = (1.0, 0.0, 0.0, 0.5)  # Red (RGBA)
inner_color = (0.0, 0.0, 1.0, 0.5)  # Blue (RGBA)

# Create multiple cubes with progressively smaller sizes and color gradient
cubes = []
num_cubes = 150
delta = 1 / num_cubes
for i in range(num_cubes):
    outer_size = np.array([1.0, 1.0, 1.0]) * (1.0 - (i * delta))  # Outer size gradually decreases
    inner_size = np.array([1.0, 1.0, 1.0]) * (1.0 - (i * delta))  # Inner size slightly smaller

    # Interpolate between the outer and inner color based on the cube index
    ratio = i / (num_cubes - 1)  # A ratio from 0 to 1 for each cube
    outer_grad = tuple(outer_color[j] * (1 - ratio) + inner_color[j] * ratio for j in range(4))  # Interpolate colors
    inner_grad = tuple(inner_color[j] * (1 - ratio) + outer_color[j] * ratio for j in range(4))  # Interpolate colors

    cubes.append(Cube(ctx, outer_size=outer_size, inner_size=inner_size, outer_color=outer_grad, inner_color=inner_grad, scale=1.0))

# Main loop
clock = pygame.time.Clock()
running = True
angle = 0
now_time = 0
start = time.perf_counter()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ctx.clear(1, 1, 1)

    outer_color = (*outer.generate_color_from_perlin_noise(value=now_time/7, format=pmma.Constants.SMALL_RGB), 0.5)
    inner_color = (*inner.generate_color_from_perlin_noise(value=now_time/10, format=pmma.Constants.SMALL_RGB), 0.5)

    for i in range(num_cubes):
        cube = cubes[i]
        ratio = i / (num_cubes - 1)  # A ratio from 0 to 1 for each cube
        outer_grad = tuple(outer_color[j] * (1 - ratio) + inner_color[j] * ratio for j in range(4))  # Interpolate colors
        inner_grad = tuple(inner_color[j] * (1 - ratio) + outer_color[j] * ratio for j in range(4))  # Interpolate colors
        cube.set_color(outer_grad, inner_grad)

    # Update rotation for each cube
    for cube in cubes:
        cube.update_rotation(angle)
        cube.render()

    # Increment angle for rotation
    angle += 0.01

    pygame.display.flip()
    clock.tick(60)
    pmma.compute()
    now_time = time.perf_counter() - start

pygame.quit()
