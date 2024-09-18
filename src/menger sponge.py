import glfw
import moderngl
import numpy as np
from pyrr import Matrix44
import time
import math
import pmma

import menger_sponge

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW can not be initialized!")

# Create a window
#monitor = glfw.get_primary_monitor()
#window = glfw.create_window(1920, 1080, "Menger Sponge", monitor, None)
window = glfw.create_window(1280, 720, "Menger Sponge", None, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window can not be created!")

near_color = pmma.ColorConverter()
far_color = pmma.ColorConverter()

glfw.make_context_current(window)
ctx = moderngl.create_context()

vertex_shader_source = """
#version 330
in vec3 in_position;
in vec3 in_normal;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
out vec3 frag_normal;
out vec3 frag_position;
void main() {
    frag_normal = in_normal;
    frag_position = vec3(model * vec4(in_position, 1.0));
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}
"""

fragment_shader_source = """
#version 330
in vec3 frag_normal;
in vec3 frag_position;
out vec3 FragColor;
uniform vec3 near_color;
uniform vec3 far_color;

void main() {
    float distance = length(frag_position);
    float t = distance;  // Adjust the divisor for the distance range
    t = clamp(t, 0.0, 1.0);
    FragColor = mix(near_color*1.5, far_color/1.5, t);
}
"""

prog = ctx.program(
    vertex_shader=vertex_shader_source,
    fragment_shader=fragment_shader_source,
)

iterations = 5
vertices, normals = menger_sponge.generate_menger_sponge(iterations)
# Convert memoryviews to NumPy arrays
vertices_np = np.array(vertices)
normals_np = np.array(normals)

# Convert NumPy arrays to bytes
vertices_bytes = vertices_np.tobytes()
normals_bytes = normals_np.tobytes()

# Create the VBO using ModernGL
vbo = ctx.buffer(vertices_bytes)
# Create the IBO (if needed)
ibo = ctx.buffer(normals_bytes)

vao = ctx.vertex_array(prog, [
    (vbo, '3f', 'in_position'),
    (ibo, '3f', 'in_normal')
])

view = Matrix44.look_at(
    (1.31, 1.31, 1.31),
    (0.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
)
projection = Matrix44.perspective_projection(45.0, 1920 / 1080, 0.1, 10.0)

prog['view'].write(view.astype('f4'))
prog['projection'].write(projection.astype('f4'))

# Set near and far colors
prog['near_color'].value = near_color.generate_color(0, format=pmma.Constants.SMALL_RGB)
prog['far_color'].value = far_color.generate_color(0, format=pmma.Constants.SMALL_RGB)

ctx.enable(moderngl.DEPTH_TEST)  # Enable depth testing
ctx.front_face = 'ccw'

while not glfw.window_should_close(window):
    glfw.poll_events()

    angle = glfw.get_time() / 2
    timer = angle/10
    prog['near_color'].value = near_color.generate_color(timer, format=pmma.Constants.SMALL_RGB)
    prog['far_color'].value = far_color.generate_color(timer, format=pmma.Constants.SMALL_RGB)
    model = Matrix44.from_x_rotation(math.sin(angle)) @ Matrix44.from_z_rotation(math.cos(angle))
    prog['model'].write(model.astype('f4'))

    ctx.clear(0.0, 0.0, 0.0, 1.0, depth=1.0)
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(window)
    time.sleep(1 / 60)

glfw.terminate()
