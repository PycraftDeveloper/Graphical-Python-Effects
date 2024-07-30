import glfw
import moderngl
import numpy as np
from pyrr import Matrix44
import time
import math
import pmma

def generate_menger_sponge(iterations):
    def recurse(level, x, y, z, size, vertices, vertex_normals):
        if level == 0:
            half = size / 2
            offsets = np.array([
                [x - half, y - half, z - half],
                [x + half, y - half, z - half],
                [x + half, y + half, z - half],
                [x - half, y + half, z - half],
                [x - half, y - half, z + half],
                [x + half, y - half, z + half],
                [x + half, y + half, z + half],
                [x - half, y + half, z + half]
            ])
            faces = np.array([
                [0, 1, 2], [2, 3, 0], # Front face
                [4, 5, 6], [6, 7, 4], # Back face
                [0, 1, 5], [5, 4, 0], # Bottom face
                [2, 3, 7], [7, 6, 2], # Top face
                [1, 2, 6], [6, 5, 1], # Right face
                [0, 3, 7], [7, 4, 0]  # Left face
            ])
            face_normals = np.array([
                [0, 0, -1], [0, 0, -1],
                [0, 0, 1], [0, 0, 1],
                [0, -1, 0], [0, -1, 0],
                [0, 1, 0], [0, 1, 0],
                [1, 0, 0], [1, 0, 0],
                [-1, 0, 0], [-1, 0, 0]
            ])
            vertices.extend(offsets[faces].reshape(-1, 3))
            vertex_normals.extend(np.repeat(face_normals, 3, axis=0))
        else:
            new_size = size / 3
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if (dx, dy, dz).count(0) < 2:
                            recurse(level - 1, x + dx * new_size, y + dy * new_size, z + dz * new_size, new_size, vertices, vertex_normals)

    vertices = []
    vertex_normals = []
    recurse(iterations, 0, 0, 0, 1, vertices, vertex_normals)
    return np.array(vertices, dtype='f4'), np.array(vertex_normals, dtype='f4')

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW can not be initialized!")

# Create a window
monitor = glfw.get_primary_monitor()
window = glfw.create_window(1920, 1080, "Menger Sponge", monitor, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window can not be created!")

near_perlin = [pmma.Perlin(), pmma.Perlin(), pmma.Perlin()]
far_perlin = [pmma.Perlin(), pmma.Perlin(), pmma.Perlin()]

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
out vec4 FragColor;
uniform vec3 near_color;
uniform vec3 far_color;

void main() {
    float distance = length(frag_position);
    float t = distance;  // Adjust the divisor for the distance range
    t = clamp(t, 0.0, 1.0);
    vec3 color = mix(near_color, far_color, t);

    vec3 result = color;
    FragColor = vec4(result, 1.0);
}
"""

prog = ctx.program(
    vertex_shader=vertex_shader_source,
    fragment_shader=fragment_shader_source,
)

iterations = 1
vertices, normals = generate_menger_sponge(iterations)
vbo = ctx.buffer(vertices.tobytes())
nbo = ctx.buffer(normals.tobytes())

vao = ctx.vertex_array(prog, [
    (vbo, '3f', 'in_position'),
    (nbo, '3f', 'in_normal')
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
near_color = (0.0, 0.0, 1.0)  # Blue
far_color = (1.0, 0.0, 0.0)   # Red
prog['near_color'].value = near_color
prog['far_color'].value = far_color

def update_buffer(vertices, normals):
    global vbo, nbo, vao
    vbo.release()
    nbo.release()
    vbo = ctx.buffer(vertices.tobytes())
    nbo = ctx.buffer(normals.tobytes())
    vao = ctx.vertex_array(prog, [
        (vbo, '3f', 'in_position'),
        (nbo, '3f', 'in_normal')
    ])

iterations = 5
vertices, normals = generate_menger_sponge(iterations)
update_buffer(vertices, normals)

ctx.enable(moderngl.DEPTH_TEST)  # Enable depth testing
ctx.front_face = 'ccw'
ctx.enable(moderngl.CULL_FACE)  # Enable face culling
ctx.cull_face = 'back'  # Cull back faces

while not glfw.window_should_close(window):
    glfw.poll_events()

    angle = glfw.get_time() / 2
    timer = angle/10
    prog['near_color'].value = (near_perlin[0].generate_1D_perlin_noise(timer, new_range=[0, 1]), near_perlin[1].generate_1D_perlin_noise(timer, new_range=[0, 1]), near_perlin[2].generate_1D_perlin_noise(timer, new_range=[0, 1]))
    prog['far_color'].value = (far_perlin[0].generate_1D_perlin_noise(timer, new_range=[0, 1]), far_perlin[1].generate_1D_perlin_noise(timer, new_range=[0, 1]), far_perlin[2].generate_1D_perlin_noise(timer, new_range=[0, 1]))
    model = Matrix44.from_x_rotation(math.sin(angle)) @ Matrix44.from_z_rotation(math.cos(angle))
    prog['model'].write(model.astype('f4'))

    ctx.clear(0.0, 0.0, 0.0, 1.0, depth=1.0)
    vao.render(moderngl.TRIANGLES)
    glfw.swap_buffers(window)
    time.sleep(1 / 60)

glfw.terminate()
