import pygame
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
from pygame.locals import *
import threading
import time
import pmma

pmma.init()


class ExpandableGrid:
    def __init__(self, initial_size, height_function):
        self.size = initial_size
        self.height_function = height_function
        self.vertices = []
        self.indices = []
        self.generate_grid()

    def generate_grid(self):
        """Initializes vertices and indices for the grid."""
        half_size = self.size // 2
        self.vertices = []

        # Generate vertices
        for z in range(-half_size, half_size + 1):
            for x in range(-half_size, half_size + 1):
                y = self.height_function(x, z)
                self.vertices.append((x, y, z))

        # Generate indices for triangle-based grid cells
        self.indices = []
        for z in range(self.size):
            for x in range(self.size):
                i0 = z * (self.size + 1) + x
                i1 = i0 + 1
                i2 = i0 + (self.size + 1)
                i3 = i2 + 1
                self.indices.extend([i0, i2, i1, i1, i2, i3])

        # Convert to numpy arrays
        self.vertices = np.array(self.vertices, dtype='f4')
        self.indices = np.array(self.indices, dtype=np.uint32)

    def expand_grid(self):
        """Expands the grid by one row and column without regenerating the entire grid."""
        self.size += 1
        half_size = self.size // 2

        # Add new vertices only on the outer edges
        new_vertices = []
        for z in range(-half_size, half_size + 1):
            for x in range(-half_size, half_size + 1):
                if abs(x) == half_size or abs(z) == half_size:
                    y = self.height_function(x, z)
                    new_vertices.append((x, y, z))

        self.vertices = np.vstack((self.vertices, np.array(new_vertices, dtype='f4')))

        # Add new indices for the expanded grid cells
        new_indices = []
        for z in range(self.size - 1, self.size):
            for x in range(self.size - 1):
                i0 = z * (self.size + 1) + x
                i1 = i0 + 1
                i2 = i0 + (self.size + 1)
                i3 = i2 + 1
                new_indices.extend([i0, i2, i1, i1, i2, i3])

        for x in range(self.size - 1, self.size):
            for z in range(self.size - 1):
                i0 = z * (self.size + 1) + x
                i1 = i0 + 1
                i2 = i0 + (self.size + 1)
                i3 = i2 + 1
                new_indices.extend([i0, i2, i1, i1, i2, i3])

        self.indices = np.concatenate((self.indices, np.array(new_indices, dtype=np.uint32)))

class Renderer:
    def __init__(self, width, height, mesh):
        pygame.init()
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((width, height), OPENGL | DOUBLEBUF, vsync=True)
        self.ctx = moderngl.create_context()
        self.mesh = mesh

        self.program = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec3 in_vert;
                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 projection;
                void main() {
                    gl_Position = projection * view * model * vec4(in_vert, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(0.3, 0.6, 0.8, 1.0);
                }
            """
        )

        self.vbo = self.ctx.buffer(self.mesh.vertices.tobytes())
        self.ibo = self.ctx.buffer(self.mesh.indices.tobytes())
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f', 'in_vert')], self.ibo)

        self.camera_pos = Vector3([0.0, 10.0, 10.0])
        self.camera_front = Vector3([0.0, -1.0, -1.0]).normalized
        self.camera_up = Vector3([0.0, 1.0, 0.0])

        self.projection = Matrix44.perspective_projection(45.0, width / height, 0.1, 100.0)
        self.ctx.viewport = (0, 0, width, height)

        self.t = threading.Thread(target=self.expander)
        self.t.start()

        self.update_pending = False

    def expander(self):
        while True:
            if self.update_pending is False:
                mesh.expand_grid()
                mesh.expand_grid()
                self.update_pending = True
            time.sleep(0.5)

    def render(self):
        self.ctx.clear(0.2, 0.3, 0.3)

        view = Matrix44.look_at(
            self.camera_pos,
            self.camera_pos + self.camera_front,
            self.camera_up
        )

        self.program['model'].write(Matrix44.identity().astype('f4').tobytes())
        self.program['view'].write(view.astype('f4').tobytes())
        self.program['projection'].write(self.projection.astype('f4').tobytes())

        self.vao.render(moderngl.TRIANGLES)

        if self.update_pending:
            self.vbo.release()
            self.ibo.release()
            self.vao.release()
            self.vbo = self.ctx.buffer(self.mesh.vertices.tobytes())
            self.ibo = self.ctx.buffer(self.mesh.indices.tobytes())
            self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f', 'in_vert')], self.ibo)
            self.update_pending = False

    def process_input(self):
        keys = pygame.key.get_pressed()
        camera_speed = 0.05
        if keys[K_w]:
            self.camera_pos += camera_speed * self.camera_front
        if keys[K_s]:
            self.camera_pos -= camera_speed * self.camera_front
        if keys[K_a]:
            self.camera_pos -= np.cross(self.camera_front, self.camera_up) * camera_speed
        if keys[K_d]:
            self.camera_pos += np.cross(self.camera_front, self.camera_up) * camera_speed

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.camera_pos += camera_speed * self.camera_front
                elif event.button == 5:  # Scroll down
                    self.camera_pos -= camera_speed * self.camera_front

        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            mouse_pos = pygame.mouse.get_pos()
            if self.last_mouse_pos:
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]
                sensitivity = 0.01
                dx *= sensitivity
                dy *= sensitivity

                # Update camera direction (Euler angles)
                self.camera_front[0] += dx
                self.camera_front[1] -= dy
            self.last_mouse_pos = mouse_pos
        else:
            self.last_mouse_pos = None

noise = pmma.Perlin()

# Usage example
initial_size = 10
def height_function(x, z):
    return noise.generate_2D_perlin_noise(x/100, z/100, new_range=[0, 1])

mesh = ExpandableGrid(initial_size, height_function)
renderer = Renderer(800, 600, mesh)
while True:
    renderer.process_input()
    renderer.render()
    pygame.display.flip()
    pmma.compute()