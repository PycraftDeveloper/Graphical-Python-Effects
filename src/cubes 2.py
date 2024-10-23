import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
import random
import pmma
import time

pmma.init()

noise = pmma.Perlin()

display = pmma.Display()
display.create()

events = pmma.Events()

# Vertex Shader with instancing
vertex_shader = '''
#version 330
uniform mat4 view_proj;
in vec3 in_vert;
in vec3 in_offset;
in vec3 in_color;
out vec4 v_color;
void main() {
    vec3 pos = in_vert;
    gl_Position = view_proj * vec4(pos + in_offset, 1.0);
    if (length(vec2(in_offset.x, in_offset.z)) > 50) {
        v_color = vec4(0, 0, 0, 0);
    } else {
        v_color = vec4(in_color*(0.2+(in_offset.y/15)), 0.5)*2;
    }
}
'''

# Fragment Shader for solid color
fragment_shader = '''
#version 330
in vec4 v_color;
out vec4 fragColor;
void main() {
    if (v_color.a == 0) {
        discard;
    }
    fragColor = v_color;
}
'''

# Compile shaders and create program
program = pmma.Registry.context.program(
    vertex_shader=vertex_shader,
    fragment_shader=fragment_shader
)

# Define a single cuboid's vertices
vertices = np.array([
    -0.5, 0.0, -0.5,
     0.5, 0.0, -0.5,
     0.5, 1.0, -0.5,
    -0.5, 1.0, -0.5,
    -0.5, 0.0,  0.5,
     0.5, 0.0,  0.5,
     0.5, 1.0,  0.5,
    -0.5, 1.0,  0.5,
], dtype='f4')

indices = np.array([
    0, 1, 2, 2, 3, 0,  # back
    4, 5, 6, 6, 7, 4,  # front
    0, 1, 5, 5, 4, 0,  # bottom
    2, 3, 7, 7, 6, 2,  # top
    0, 3, 7, 7, 4, 0,  # left
    1, 2, 6, 6, 5, 1,  # right
], dtype='i4')

# Create Vertex Buffer Object and Element Buffer Object
vbo = pmma.Registry.context.buffer(vertices.tobytes())
ebo = pmma.Registry.context.buffer(indices.tobytes())

# Create instance data for offsets, heights, and colors
def create_instance_data(n):
    offsets = []
    colors = []
    for i in range(n):
        for j in range(n):
            offsets.append([i - n / 2, 0, j - n / 2])
            colors.append([random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)])
    return np.array(offsets, dtype='f4'), np.array(colors, dtype='f4')

n = 100  # Adjust grid size for testing
offsets, colors = create_instance_data(n)

# Create buffers for instance data
offset_buffer = pmma.Registry.context.buffer(offsets.tobytes())
color_buffer = pmma.Registry.context.buffer(colors.tobytes())

# Create Vertex Array Object with instancing
vao = pmma.Registry.context.vertex_array(
    program,
    [
        (vbo, '3f', 'in_vert'),
        (offset_buffer, '3f/i', 'in_offset'),
        (color_buffer, '3f/i', 'in_color')
    ],
    ebo
)

# Create view and projection matrices
view = Matrix44.look_at(
    eye=Vector3([n/5, n/5, n/5]),
    target=Vector3([0, 0, 0]),
    up=Vector3([0, 1, 0])
)
proj = Matrix44.perspective_projection(90, display.get_width() / display.get_height(), 0.1, 1000.0)
view_proj = proj * view

# Uniform locations
view_proj_loc = program['view_proj']
view_proj_loc.write(view_proj.astype('f4').tobytes())

# Main loop
clock = pygame.time.Clock()
running = True
angle = 0.0

start = time.perf_counter()
now_time = 0
while pmma.Registry.running:
    # Event handling
    events.handle()

    # Clear the screen
    display.clear(0, 0, 0)
    pmma.Registry.context.enable(moderngl.DEPTH_TEST | moderngl.BLEND)

    # Rotate the camera around the grid
    angle += 0.01
    x = 55 * np.sin(angle/2)
    y = 55 * np.cos(angle/2)
    view = Matrix44.look_at(
        eye=Vector3([x, 10, y]), # 1+noise.generate_2D_perlin_noise((int(x)/20)+now_time, (int(y)/20)+now_time, new_range=[0, 4])
        target=Vector3([0, 0, 0]),
        up=Vector3([0, 1, 0])
    )

    view_proj = proj * view
    view_proj_loc.write(view_proj.astype('f4').tobytes())

    # Update cube heights dynamically
    #i = 0
    #print(noise.generate_2D_perlin_noise((i%n)+now_time, (i//n)+now_time, new_range=[0, 4]))
    new_heights = np.array([[offset[0], noise.generate_2D_perlin_noise(((i%n)/30)+now_time, ((i//n)/30)+now_time, new_range=[0, 4.32])**2, offset[2]]  for i, offset in enumerate(offsets)], dtype='f4')
    offset_buffer.write(new_heights.tobytes())

    # Render all cuboids with a single draw call
    display.get_3D_hardware_accelerated_surface()
    vao.render(moderngl.TRIANGLES, instances=len(offsets))

    pmma.compute()

    display.refresh()
    now_time = (time.perf_counter()-start)/10

# Cleanup
import traceback
try:
    pmma.quit()
except Exception as error:
    print(traceback.format_exc())
pygame.quit()
