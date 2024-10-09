import pygame
import numpy as np
from noise import pnoise2
import moderngl
from pyrr import Matrix44
import time
import pmma
import threading
import math

pmma.init()

# Constants for the terrain
WIDTH, HEIGHT = 1920, 1080
GRID_SIZE = 2000#1000  # Number of vertices along one side of the terrain
SCALE = 0.25#0.5     # Distance between vertices in the grid
AMPLITUDE = 100#50 # Height amplitude for the noise

# Initialize Pygame and ModernGL context
pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN, vsync=1)
context = moderngl.create_context()
clock = pygame.time.Clock()

# Shader Programs
vertex_shader = """
#version 330

// Uniform variables passed in from the main program
uniform mat4 mvp;         // Model-View-Projection matrix
uniform float height;     // Maximum height value for scaling grayscale
uniform float time;       // Time variable for animation

// Input variables from the vertex buffer
in vec3 in_vert;          // Vertex position
in vec3 in_norm;          // Normal vector

// Output color to be passed to the fragment shader
out vec4 v_color;

void main() {
    // Apply the transformation matrix to the vertex position
    vec3 position = in_vert;
    // Compute the grayscale value based on the height of the vertex
    float grayscale = in_vert.y / height;
    v_color = vec4(0, grayscale, 0, 1.0);  // Set base color to grayscale value

    // Calculate the radius from the center of the terrain (using the x and z coordinates)
    float radius = length(in_vert.xz);

    // Determine the maximum radius for the animation based on the terrain size
    float max_radius = 250.0;  // Adjust as necessary depending on the grid size

    float pi = 3.141592653589793238462643383279502884197169/2;

    // Use the sin function to grow and shrink the terrain over time
    float growth_factor = (1 + sin(time - pi)) / 2 * max_radius;

    // Fade out effect for far away points
    float fade_start = 200;
    float fade_end = 250;
    float fade_factor = 1-smoothstep(fade_start, fade_end, radius);

    // Apply the animation effect
    if (radius < growth_factor) {
        // Inside the growing region
        if (in_vert.y < 20) {
            v_color = vec4(0, 0, 1, fade_factor);
            position.y = 20;
        } else {
            v_color = vec4(0, grayscale, 0, fade_factor);
        }
    } else if (abs(radius - growth_factor) < 5.0) {
        // Highlight the expanding edge with an orange color
        v_color = vec4(1.0, 0.65, 0.0, fade_factor);  // Orange color (#FFA500)
    } else {
        // Set the final color to black with fade out effect
        v_color = vec4(0, 0, 0, 0.0);
    }

    gl_Position = (mvp * vec4(position, 1.0)) * 50;
}
"""

fragment_shader = """
#version 330
in vec4 v_color;
out vec4 fragColor;

void main() {
    fragColor = vec4(v_color);
}
"""

# Create a ModernGL program
program = context.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
mvp = program['mvp']
program['height'].value = float(AMPLITUDE)

def generate_terrain(grid_size, scale, amplitude):
    vertices = []
    indices = []

    # Generate a flat grid of points with zero heights (height is set later)
    half_grid = grid_size // 2
    for x in range(grid_size):
        for z in range(grid_size):
            # Create the vertex position (x * scale, height, z * scale)
            vertices.append([(x - half_grid) * scale, 0, (z - half_grid) * scale])

    # Generate triangle indices for the grid
    for x in range(grid_size - 1):
        for z in range(grid_size - 1):
            # Calculate indices of the four corners of the cell
            top_left = x * grid_size + z
            top_right = top_left + 1
            bottom_left = top_left + grid_size
            bottom_right = bottom_left + 1

            # Create two triangles for the cell
            indices.extend([top_left, bottom_left, top_right])  # First triangle
            indices.extend([top_right, bottom_left, bottom_right])  # Second triangle

    return np.array(vertices, dtype='f4'), np.array(indices, dtype='i4')

vertices, indices = generate_terrain(GRID_SIZE, SCALE, AMPLITUDE)
noise = pmma.Perlin(octaves=8)

def apply_noise(noise, vertices, amplitude):
    for i in range(len(vertices)):
        x, y, z = vertices[i]
        y = noise.generate_2D_perlin_noise(x/400, z/400, new_range=[0, amplitude])
        vertices[i] = [x, y, z]

    return vertices

vertices = apply_noise(noise, vertices, AMPLITUDE)

class Terrain:
    def __init__(self, vertices):
        self.vertices = vertices

    def apply(self):
        vbo.write(self.vertices.tobytes())

    def update(self):
        noise = pmma.Perlin(octaves=8)

        self.vertices = apply_noise(noise, vertices, AMPLITUDE)

    def terrain_changer(self):
        while True:
            s = time.perf_counter()
            self.update()
            e = time.perf_counter()
            if 10-(e-s) > 0:
                time.sleep(10-(e-s))

terrain = Terrain(vertices)

terrain_changer = threading.Thread(target=terrain.terrain_changer)
terrain_changer.daemon = True
terrain_changer.start()

# Create ModernGL buffers
vbo = context.buffer(vertices.tobytes())
ibo = context.buffer(indices.tobytes())
vao = context.simple_vertex_array(program, vbo, 'in_vert', index_buffer=ibo)

# Camera parameters
camera_pos = np.array([0.0, 100.0, 25.0])
camera_front = np.array([0.0, 0.0, -1.0])
camera_up = np.array([0.0, 1.0, 0.0])
camera_speed = 10

# Mouse control
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
yaw, pitch = -90.0, 0.0
last_x, last_y = WIDTH // 2, HEIGHT // 2

# Main render loop
running = True
now_time = 0
start = time.perf_counter()
context.front_face = 'cw'
context.enable(moderngl.DEPTH_TEST)
context.enable(moderngl.BLEND)
context.enable(moderngl.CULL_FACE)

def get_height_at_origin(vertices, grid_size):
    # Calculate the index for the origin in the vertex array
    index_at_origin = (grid_size // 2) * grid_size + (grid_size // 2)

    # Access the height (Y coordinate) at the origin
    height_at_origin = vertices[index_at_origin][1]  # [1] for the Y component

    return height_at_origin

TAU = math.pi * 2

camera_height = get_height_at_origin(vertices, GRID_SIZE)

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
    x = time.time() * 100
    dx, dy = x - last_x, last_y - y
    last_x, last_y = x, y

    camera_pos[0] = 0
    camera_pos[1] = camera_height + 1
    camera_pos[2] = 0


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
    projection = Matrix44.perspective_projection(90.0, WIDTH / HEIGHT, 0.1, 1000000.0)
    mvp.write((projection * view).astype('f4').tobytes())

    # Render the terrain
    context.clear(0.1, 0.2, 0.3)
    vao.render(moderngl.TRIANGLES)
    pygame.display.flip()
    clock.tick(60)

    timer = (TAU/10) * now_time

    program['time'].value = timer

    now_time = time.perf_counter() - start
    if (TAU/10) * now_time > TAU:
        start = time.perf_counter()

        terrain.apply()

        camera_height = get_height_at_origin(vertices, GRID_SIZE)

    pmma.compute()

pygame.quit()
