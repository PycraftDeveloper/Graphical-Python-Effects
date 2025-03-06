import pygame
import moderngl
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL
from pyrr import Matrix44


class Cube:
    def __init__(self, ctx, width=1.0, outer_color=(1.0, 0.0, 0.0, 1.0), inner_color=(0.0, 1.0, 0.0, 1.0), scale=1.0):
        self.ctx = ctx
        self.width = width
        self.outer_color = outer_color
        self.inner_color = inner_color
        self.scale = scale  # The scale factor applied in the shader

        # Define the outer and inner cube vertices with their respective colors
        outer_vertices = np.array([
            # Outer cube vertices (x, y, z, r, g, b, a)
            -0.5, -0.5, -0.5, *outer_color,
            0.5, -0.5, -0.5, *outer_color,
            0.5, 0.5, -0.5, *outer_color,
            -0.5, 0.5, -0.5, *outer_color,
            -0.5, -0.5, 0.5, *outer_color,
            0.5, -0.5, 0.5, *outer_color,
            0.5, 0.5, 0.5, *outer_color,
            -0.5, 0.5, 0.5, *outer_color,
        ], dtype='f4')

        inner_vertices = np.array([
            # Inner cube vertices (x, y, z, r, g, b, a)
            -0.5 + width, -0.5 + width, -0.5 + width, *inner_color,
            0.5 - width, -0.5 + width, -0.5 + width, *inner_color,
            0.5 - width, 0.5 - width, -0.5 + width, *inner_color,
            -0.5 + width, 0.5 - width, -0.5 + width, *inner_color,
            -0.5 + width, -0.5 + width, 0.5 - width, *inner_color,
            0.5 - width, -0.5 + width, 0.5 - width, *inner_color,
            0.5 - width, 0.5 - width, 0.5 - width, *inner_color,
            -0.5 + width, 0.5 - width, 0.5 - width, *inner_color,
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

    def set_outer_color(self, color):
        self.outer_color = color
        self.vertices[::7] = color[0]
        self.vertices[1::7] = color[1]
        self.vertices[2::7] = color[2]
        self.vertices[3::7] = color[3]
        self.vbo.write(self.vertices)

    def set_inner_color(self, color):
        self.inner_color = color
        self.vertices[::7] = color[0]
        self.vertices[1::7] = color[1]
        self.vertices[2::7] = color[2]
        self.vertices[3::7] = color[3]
        self.vbo.write(self.vertices)

    def update_rotation(self, angle, axis):
        rotation = Matrix44.from_eulers((angle, angle, 0), dtype='f4')
        self.rotation_matrix = rotation

    def render(self):
        self.ctx.clear()
        self.program['model'].write(self.rotation_matrix)
        self.program['scale'].value = self.scale  # Pass the scale to the shader
        self.vao.render(moderngl.TRIANGLES)


# Initialize Pygame and ModernGL
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
ctx = moderngl.create_context()

ctx.enable(moderngl.BLEND)
ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

# Create multiple cubes with progressively smaller sizes
cubes = []
num_cubes = 5
for i in range(num_cubes):
    scale = 1.0 - (i * 0.1)  # Make each cube smaller by 10%
    outer_color = (1.0 - i * 0.2, i * 0.2, 0.0, 0.5)  # Gradient color for outer part
    inner_color = (i * 0.2, 1.0 - i * 0.2, 0.0, 0.5)  # Gradient color for inner part
    cubes.append(Cube(ctx, width=0.1, outer_color=outer_color, inner_color=inner_color, scale=scale))

# Main loop
clock = pygame.time.Clock()
running = True
angle = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update rotation for each cube
    for cube in cubes:
        cube.update_rotation(angle, axis='y')
        cube.render()

    # Increment angle for rotation
    angle += 0.01

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
