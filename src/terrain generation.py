import pygame
import numpy as np
from noise import pnoise2
import moderngl
from pyrr import Matrix44

# Constants for the terrain
WIDTH, HEIGHT = 1920, 1080
GRID_SIZE = 500  # Number of vertices along one side of the terrain
SCALE = 2.0     # Distance between vertices in the grid
AMPLITUDE = 5 # Height amplitude for the noise

# Initialize Pygame and ModernGL context
pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN, vsync=1)
context = moderngl.create_context()
clock = pygame.time.Clock()

# Shader Programs
vertex_shader = """
#version 330
uniform mat4 mvp;
uniform float height;
in vec3 in_vert;
in vec3 in_norm;
out vec3 v_color;

void main() {
    gl_Position = mvp * vec4(in_vert, 1.0);
    v_color = vec3(1, 1, 1) + in_norm * 0.5;
    v_color *= in_vert.y/height;
}
"""

fragment_shader = """
#version 330
in vec3 v_color;
out vec4 fragColor;

void main() {
    fragColor = vec4(v_color, 1.0);
}
"""

# Create a ModernGL program
program = context.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
mvp = program['mvp']
program['height'].value = float(AMPLITUDE)

# Generate terrain vertices and indices
def generate_terrain(grid_size, scale, amplitude):
    vertices = []
    indices = []

    # Generate a flat grid of points with noise for heights
    for x in range(grid_size):
        for z in range(grid_size):
            # Generate height using Perlin noise
            y = amplitude * pnoise2(x / 10.0, z / 10.0, octaves=4)
            vertices.append([x * scale, y, z * scale])

    # Generate triangle indices
    for x in range(grid_size - 1):
        for z in range(grid_size - 1):
            i = x * grid_size + z
            indices.extend([i, i + grid_size, i + 1, i + 1, i + grid_size, i + grid_size + 1])

    return np.array(vertices, dtype='f4'), np.array(indices, dtype='i4')

vertices, indices = generate_terrain(GRID_SIZE, SCALE, AMPLITUDE)

# Create ModernGL buffers
vbo = context.buffer(vertices.tobytes())
ibo = context.buffer(indices.tobytes())
vao = context.simple_vertex_array(program, vbo, 'in_vert', index_buffer=ibo)

# Camera parameters
camera_pos = np.array([0.0, 10.0, 25.0])
camera_front = np.array([0.0, 0.0, -1.0])
camera_up = np.array([0.0, 1.0, 0.0])
camera_speed = 0.1

# Mouse control
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
yaw, pitch = -90.0, 0.0
last_x, last_y = WIDTH // 2, HEIGHT // 2

# Main render loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Camera controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera_pos += camera_speed * camera_front
    if keys[pygame.K_s]:
        camera_pos -= camera_speed * camera_front
    if keys[pygame.K_a]:
        camera_pos -= np.cross(camera_front, camera_up) * camera_speed
    if keys[pygame.K_d]:
        camera_pos += np.cross(camera_front, camera_up) * camera_speed

    # Mouse look controls
    x, y = pygame.mouse.get_pos()
    dx, dy = x - last_x, last_y - y
    last_x, last_y = x, y

    sensitivity = 0.1
    dx *= sensitivity
    dy *= sensitivity

    yaw += dx
    pitch += dy
    if pitch > 89.0:
        pitch = 89.0
    if pitch < -89.0:
        pitch = -89.0

    # Update camera direction
    front = np.array([
        np.cos(np.radians(yaw)) * np.cos(np.radians(pitch)),
        np.sin(np.radians(pitch)),
        np.sin(np.radians(yaw)) * np.cos(np.radians(pitch))
    ])
    camera_front = front / np.linalg.norm(front)

    # Compute view and projection matrices
    view = Matrix44.look_at(camera_pos, camera_pos + camera_front, camera_up)
    projection = Matrix44.perspective_projection(45.0, WIDTH / HEIGHT, 0.1, 10000.0)
    mvp.write((projection * view).astype('f4').tobytes())

    # Render the terrain
    context.clear(0.1, 0.2, 0.3)
    vao.render()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
