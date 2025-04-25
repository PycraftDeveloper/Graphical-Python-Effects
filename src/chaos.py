import pygame
import numpy as np
import moderngl as mgl
from pyrr import Matrix44
import pmma

pmma.init()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# Initialize ModernGL context
ctx = mgl.create_context()

# Vertex Shader
vertex_shader = """
#version 330
uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

in vec3 in_position;       // Base sphere vertex
in vec3 instance_position; // Small sphere instance position
in vec3 instance_color;    // Small sphere instance color
in float instance_radius;  // Small sphere instance radius

out vec3 frag_color;

void main() {
    vec3 scaled_position = in_position * instance_radius; // Scale small sphere
    vec3 world_position = scaled_position + instance_position; // Translate to instance position
    gl_Position = projection * view * model * vec4(world_position, 1.0);
    frag_color = instance_color;
}
"""

# Fragment Shader
fragment_shader = """
#version 330
in vec3 frag_color;
out vec4 color;

void main() {
    color = vec4(frag_color, 1.0);
}
"""

# Compile shaders and link program
program = ctx.program(
    vertex_shader=vertex_shader,
    fragment_shader=fragment_shader,
)

# Uniforms
projection = program['projection']
view = program['view']
model = program['model']

# Generate base sphere geometry (triangular mesh for the small spheres)
def generate_sphere_mesh(radius, segments):
    vertices = []
    indices = []
    for i in range(segments):
        theta1 = np.pi * i / segments
        theta2 = np.pi * (i + 1) / segments

        for j in range(segments):
            phi1 = 2 * np.pi * j / segments
            phi2 = 2 * np.pi * (j + 1) / segments

            # Sphere vertices
            x1, y1, z1 = radius * np.sin(theta1) * np.cos(phi1), radius * np.sin(theta1) * np.sin(phi1), radius * np.cos(theta1)
            x2, y2, z2 = radius * np.sin(theta2) * np.cos(phi1), radius * np.sin(theta2) * np.sin(phi1), radius * np.cos(theta2)
            x3, y3, z3 = radius * np.sin(theta2) * np.cos(phi2), radius * np.sin(theta2) * np.sin(phi2), radius * np.cos(theta2)
            x4, y4, z4 = radius * np.sin(theta1) * np.cos(phi2), radius * np.sin(theta1) * np.sin(phi2), radius * np.cos(theta1)

            # Append vertices
            vertices.extend([(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4)])

            # Add triangle indices
            base = len(vertices) - 4
            indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    return np.array(vertices, dtype='f4'), np.array(indices, dtype='i4')

sphere_vertices, sphere_indices = generate_sphere_mesh(1.0, 16)

# Create buffers for sphere geometry
vbo_sphere = ctx.buffer(sphere_vertices.tobytes())
ibo_sphere = ctx.buffer(sphere_indices.tobytes())

# Distribute points on a sphere (outer sphere)
def generate_cube_grid(grid_size=5, spacing=2.0):
    """ Generates small sphere positions arranged in a cubic grid. """
    positions = []
    half_extent = (grid_size - 1) / 2 * spacing  # Centering the cube

    for x in range(grid_size):
        for y in range(grid_size):
            for z in range(grid_size):
                positions.append((
                    x * spacing - half_extent,
                    y * spacing - half_extent,
                    z * spacing - half_extent
                ))

    return np.array(positions, dtype='f4')

# Generate instance data
instance_positions = generate_cube_grid(grid_size=30, spacing=1.0)
instance_colors = np.random.uniform(0.0, 1.0, (len(instance_positions), 3)).astype('f4')
instance_radii = np.random.uniform(0.1, 0.1, (len(instance_positions),)).astype('f4')

vbo_instance_position = ctx.buffer(instance_positions.tobytes())
vbo_instance_color = ctx.buffer(instance_colors.tobytes())
vbo_instance_radius = ctx.buffer(instance_radii.tobytes())

# Create VAO
vao = ctx.vertex_array(
    program,
    [
        (vbo_sphere, '3f', 'in_position'),
        (vbo_instance_position, '3f/i', 'instance_position'),
        (vbo_instance_color, '3f/i', 'instance_color'),
        (vbo_instance_radius, '1f/i', 'instance_radius'),
    ],
    index_buffer=ibo_sphere,
)

# Projection and view matrices
projection_matrix = Matrix44.perspective_projection(45.0, 1920 / 1080, 0.1, 100.0)
view_matrix = Matrix44.look_at(
    eye=(1.0, 1.0, 1.0),
    target=(0.0, 0.0, 0.0),
    up=(0.0, 1.0, 0.0)
)
model_matrix = Matrix44.identity()

# Main loop
running = True
angle = 0.0
x_noise = pmma.Perlin(do_prefill=False)
y_noise = pmma.Perlin(do_prefill=False)
z_noise = pmma.Perlin(do_prefill=False)
general = pmma.General()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    ctx.clear(0, 0, 0)
    ctx.enable(mgl.DEPTH_TEST)

    # Rotate model matrix
    angle += 0.01
    model_matrix = Matrix44.from_eulers((angle, angle / 2, angle / 3))

    # Normalize instance positions for noise
    norm_x = instance_positions[:, 0] / 25 + general.get_application_run_time() / 25
    norm_y = instance_positions[:, 1] / 25 + general.get_application_run_time() / 25
    norm_z = instance_positions[:, 2] / 25 + general.get_application_run_time() / 25

    # Vectorized Perlin noise generation
    vec_perlin_x = np.vectorize(x_noise.generate_2D_perlin_noise, otypes=['f4'])
    vec_perlin_y = np.vectorize(y_noise.generate_2D_perlin_noise, otypes=['f4'])
    vec_perlin_z = np.vectorize(z_noise.generate_2D_perlin_noise, otypes=['f4'])

    # Compute noise values efficiently
    r_values = (vec_perlin_x(norm_x, norm_y) + 1) / 2
    g_values = (vec_perlin_y(norm_y, norm_z) + 1) / 2
    b_values = (vec_perlin_z(norm_z, norm_x) + 1) / 2

    # Assign noise values to instance colors
    instance_colors[:, 0] = r_values
    instance_colors[:, 1] = g_values
    instance_colors[:, 2] = b_values

    # Update the color buffer in one go
    vbo_instance_color.write(instance_colors.tobytes())

    # Update uniforms
    projection.write(projection_matrix.astype('f4').tobytes())
    view.write(view_matrix.astype('f4').tobytes())
    model.write(model_matrix.astype('f4').tobytes())

    # Render spheres
    vao.render(instances=len(instance_positions))

    # Swap buffers
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
