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

import terrain_generator

# Constants for the terrain
WIDTH, HEIGHT = 1920, 1080
GRID_SIZE = 1#1000  # Number of vertices along one side of the terrain
SCALE = 0.1#0.5     # Distance between vertices in the grid
AMPLITUDE = 100#50 # Height amplitude for the noise

def load_texture(filepath, context):
    texture = pygame.image.load(filepath)
    texture_data = pygame.image.tostring(texture, "RGB", True)
    return context.texture(texture.get_size(), 3, texture_data)

def generate_perlin_noise(noise, grid_size, scale, amplitude):
    noise_values = np.empty(grid_size * grid_size, dtype=np.float32)

    for i in range(grid_size):
        for j in range(grid_size):
            y = noise.generate_2D_perlin_noise(i / 2500.0, j / 2500.0, new_range=[0, amplitude])
            noise_values[i * grid_size + j] = y

    return noise_values

def generate_terrain(noise, grid_size, scale, amplitude):
    noise_values = generate_perlin_noise(noise, grid_size, scale, amplitude)
    return terrain_generator.generate_terrain(noise_values, grid_size, scale)

# Initialize Pygame and ModernGL context
pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN, vsync=1)
context = moderngl.create_context()
clock = pygame.time.Clock()

class ExpandableMesh:
    def __init__(self, initial_size, height_function):
        self.size = initial_size
        self.height_function = height_function
        self.vertices = []
        self.tex_coords = []
        self.indices = []

        self.generate_initial_grid()

    def generate_initial_grid(self):
        half_size = self.size // 2
        for z in range(-half_size, half_size + 1):
            for x in range(-half_size, half_size + 1):
                y = self.height_function(x, z)
                self.vertices.append((x, y, z))
                self.tex_coords.append(((x + half_size) / self.size, (z + half_size) / self.size))
        self.generate_indices()

        self.vbo = context.buffer(np.array(self.vertices, dtype='f4').tobytes())
        self.ibo = context.buffer(self.indices.tobytes())

    def generate_indices(self):
        n = self.size
        indices = []
        for z in range(n - 1):
            for x in range(n - 1):
                i0 = z * n + x
                i1 = i0 + 1
                i2 = i0 + n
                i3 = i2 + 1
                indices.extend([i0, i1, i2, i2, i1, i3])
        self.indices = np.array(indices, dtype=np.uint32)

    def expand_grid(self):
        self.size += 1
        new_half_size = self.size // 2
        for x in range(-new_half_size, new_half_size + 1):
            for z in [-new_half_size, new_half_size]:
                if (x, z) not in self.vertex_positions():
                    y = self.height_function(x, z)
                    self.vertices.append((x, y, z))
                    self.tex_coords.append(((x + new_half_size) / self.size, (z + new_half_size) / self.size))

        for z in range(-new_half_size + 1, new_half_size):
            for x in [-new_half_size, new_half_size]:
                if (x, z) not in self.vertex_positions():
                    y = self.height_function(x, z)
                    self.vertices.append((x, y, z))
                    self.tex_coords.append(((x + new_half_size) / self.size, (z + new_half_size) / self.size))

        self.generate_indices()

        self.vbo.update(np.array(self.vertices, dtype='f4').tobytes())
        self.ibo.update(self.indices.tobytes())

    def vertex_positions(self):
        return set((vx, vz) for vx, _, vz in self.vertices)

# Shader Programs
vertex_shader = """
#version 330

// Uniform variables passed in from the main program
uniform mat4 mvp;         // Model-View-Projection matrix
uniform float time;       // Time variable for animation

uniform sampler2D grass_texture;
uniform sampler2D rock_texture;

// Input variables from the vertex buffer
in vec3 in_vert;
in vec3 in_norm;
in vec2 in_texcoord;

// Output color to be passed to the fragment shader
out vec4 v_color;

void main() {
    // Apply the transformation matrix to the vertex position
    vec3 position = in_vert;
    // Compute the grayscale value based on the height of the vertex
    float slope = in_norm.y;

    // Mix between grass and rock textures based on the slope
    vec4 grass_color = texture(grass_texture, in_texcoord);
    vec4 rock_color = texture(rock_texture, in_texcoord);

    // Blend grass and rock based on slope (higher slope means more rock)
    vec3 color = mix(grass_color, rock_color, 1-slope).rgb;

    // Calculate the radius from the center of the terrain (using the x and z coordinates)
    float radius = length(in_vert.xz);

    // Determine the maximum radius for the animation based on the terrain size
    float max_radius = 700.0;  // Adjust as necessary depending on the grid size 250

    float pi = 3.141592653589793238462643383279502884197169/2;

    // Use the sin function to grow and shrink the terrain over time
    float growth_factor = (1 + sin(time - pi)) / 2 * max_radius;

    // Fade out effect for far away points
    float fade_start = 60; // 60
    float fade_end = 700; // 85
    float fade_factor = 1-smoothstep(fade_start, fade_end, radius);

    // Apply the animation effect
    if (radius < growth_factor) {
        // Inside the growing region
        if (in_vert.y < 20) {
            v_color = vec4(0, 0, 1, fade_factor);
            position.y = 20;
        } else {
            v_color = vec4(color, fade_factor);
        }
    } else {
        // Set the final color to black with fade out effect
        v_color = vec4(0, 0, 0, 0.0);
    }

    if (abs(radius - growth_factor) < 5.0) {
        // Highlight the expanding edge with an orange color
        v_color = vec4(1.0, 0.65, 0.0, fade_factor);  // Orange color (#FFA500)
    }

    gl_Position = 50*(mvp * vec4(position, 1.0)); // *50
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

noise = pmma.Perlin(octaves=8, do_prefill=False)

vertices, indices, normals, texcoords = generate_terrain(noise, GRID_SIZE, SCALE, AMPLITUDE)

class Terrain:
    def __init__(self, vertices, normals, indices, texcoords):
        self.vertices = vertices
        self.normals = normals
        self.indices = indices
        self.texcoords = texcoords

        self.noise = pmma.Perlin(octaves=4, do_prefill=False)

    def apply(self):
        # Combine vertex positions and normals into a single array
        vertex_data = np.hstack([self.vertices, self.normals, self.texcoords]).astype('f4')
        #vbo.write(vertex_data.tobytes())  # Update VBO with both position and normal data

    def update(self):
        self.noise = pmma.Perlin(octaves=4)

        self.vertices, self.indices, self.normals, self.texcoords = generate_terrain(self.noise, GRID_SIZE, SCALE, AMPLITUDE)

    def terrain_changer(self):
        while True:
            s = time.perf_counter()
            self.update()
            e = time.perf_counter()
            if 10-(e-s) > 0:
                time.sleep(10-(e-s))

terrain = Terrain(vertices, normals, indices, texcoords)

terrain_changer = threading.Thread(target=terrain.terrain_changer)
terrain_changer.daemon = True
#terrain_changer.start()

# Create ModernGL buffers

grass_texture = load_texture(r"H:\Documents\GitHub\Graphical-Python-Effects\src\resources\grass.png", context)
grass_texture.repeat_x = True
grass_texture.repeat_y = True
rock_texture = load_texture(r"H:\Documents\GitHub\Graphical-Python-Effects\src\resources\rock.png", context)
rock_texture.repeat_x = True
rock_texture.repeat_y = True

program['grass_texture'].value = 0
program['rock_texture'].value = 1

grass_texture.use(location=0)
rock_texture.use(location=1)

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

    if height_at_origin < 20:
        height_at_origin = 20

    return height_at_origin

TAU = math.pi * 2

camera_height = get_height_at_origin(vertices, GRID_SIZE)

def height(x, z):
    return 0

e = ExpandableMesh(6, height)
vao1 = context.simple_vertex_array(program, e.vbo, 'in_vert', 'in_norm', 'in_texcoord', index_buffer=e.ibo)
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

    camera_pos[0] = 0
    camera_pos[1] = camera_height + 5#1
    camera_pos[2] = 0

    # Sensitivity adjustment
    sensitivity = 0.1
    dx *= sensitivity
    dy *= sensitivity

    yaw += dx
    pitch += dy

    # Clamp the pitch to prevent flipping
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

    # Reset mouse to the center of the screen
    pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
    last_x, last_y = WIDTH // 2, HEIGHT // 2

    # Compute view and projection matrices
    view = Matrix44.look_at(camera_pos, camera_pos + camera_front, camera_up)
    projection = Matrix44.perspective_projection(90.0, WIDTH / HEIGHT, 0.1, 1000000.0)
    mvp.write((projection * view).astype('f4').tobytes())

    # Render the terrain
    context.clear(0.1, 0.2, 0.3)
    vao1.render(moderngl.LINES)
    pygame.display.flip()
    clock.tick(60)

    timer = (TAU/10) * now_time

    program['time'].value = timer/2

    now_time = time.perf_counter() - start
    #if (TAU/10) * now_time/2 > TAU:
        #start = time.perf_counter()

        #terrain.apply()

        #camera_height = get_height_at_origin(terrain.vertices, GRID_SIZE)

    pmma.compute()

pygame.quit()
