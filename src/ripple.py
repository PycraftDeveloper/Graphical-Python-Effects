import moderngl
import pygame
import numpy as np
import time
import pyrr  # For matrix transformations
import pmma

# Initialize Pygame
pmma.init()
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)

# Initialize ModernGL Context
ctx = moderngl.create_context()

# Mesh Parameters
n = 500  # Grid resolution
size = 2.0  # World-space size of the mesh
spacing = size / (n - 1)

# Generate Mesh Vertices
vertices = []
indices = []
for i in range(n):
    for j in range(n):
        x = -1.0 + j * spacing
        z = -1.0 + i * spacing
        y = 0.0  # Initial height
        vertices.extend([x, y, z])

# Generate Indices for Triangle Strip
for i in range(n - 1):
    for j in range(n):
        indices.append(i * n + j)
        indices.append((i + 1) * n + j)
indices = np.array(indices, dtype=np.uint32)

# Convert to Numpy Array
vertices = np.array(vertices, dtype=np.float32)

# Create Buffers
vbo = ctx.buffer(vertices)
ibo = ctx.buffer(indices)

# Camera and Projection Matrices
proj_matrix = pyrr.matrix44.create_perspective_projection(45.0, screen.get_width() / screen.get_height(), 0.1, 10.0)
view_matrix = pyrr.matrix44.create_look_at(
    eye=[0, 1.5 / 2, 3 / 2.3],      # Camera position
    target=[0, 0, 0],      # Looking at the center
    up=[0, 1, 0]           # Up direction
)

# Shader Program
prog = ctx.program(
    vertex_shader="""
    #version 330
    uniform float time;
    uniform mat4 proj;
    uniform mat4 view;
    uniform float wave_strength;
    uniform vec3 color1;
    uniform vec3 color2;

    in vec3 in_vert;
    out vec3 v_color;

    void main() {
        float dist = length(in_vert.xz);
        float scale = 1.0 - smoothstep(0.0, 1.2, dist);  // Stronger waves near center
        float wave = sin(6.0 * dist - time * 3.0) * wave_strength * scale;

        vec3 pos = vec3(in_vert.x, in_vert.y + wave, in_vert.z);

        gl_Position = proj * view * vec4(pos, 1.0);

        float t = 0.5 + 0.5 * (wave / wave_strength);
        v_color = mix(color1, color2, t);
    }
    """,
    fragment_shader="""
    #version 330
    in vec3 v_color;
    out vec4 fragColor;

    void main() {
        fragColor = vec4(v_color, 1.0);
    }
    """
)

# Pass Projection & View Matrices
prog["proj"].write(proj_matrix.astype("f4").tobytes())
prog["view"].write(view_matrix.astype("f4").tobytes())

# Set Default Uniform Values
prog["wave_strength"].value = 0.15  # Control displacement amount
color_one = pmma.ColorConverter()
color_two = pmma.ColorConverter()
prog["color1"].value = color_one.generate_color_from_perlin_noise(format=pmma.Constants.SMALL_RGB)
prog["color2"].value = color_two.generate_color_from_perlin_noise(format=pmma.Constants.SMALL_RGB)

# Vertex Array Object
vao = ctx.vertex_array(prog, [(vbo, "3f", "in_vert")], index_buffer=ibo)

# Time Tracking
start_time = time.time()

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                prog["wave_strength"].value += 0.05  # Increase wave effect
            elif event.key == pygame.K_DOWN:
                prog["wave_strength"].value -= 0.05  # Decrease wave effect

    prog["color1"].value = color_one.generate_color_from_perlin_noise(value=(time.time() - start_time)/7, format=pmma.Constants.SMALL_RGB)
    prog["color2"].value = color_two.generate_color_from_perlin_noise(value=(time.time() - start_time)/7, format=pmma.Constants.SMALL_RGB)
    prog["time"].value = time.time() - start_time

    # Render
    ctx.clear(0.1, 0.1, 0.1)
    vao.render(moderngl.TRIANGLE_STRIP)
    pygame.display.flip()

    pmma.compute()

pygame.quit()
