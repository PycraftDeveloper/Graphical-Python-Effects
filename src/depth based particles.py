import numpy as np
import pyglet
from pyglet.gl import *
import moderngl as GL
from pyrr import Matrix44, matrix44

# Initialize Pyglet window
width, height = 800, 600
window = pyglet.window.Window(width, height, "Particle System with Depth of Field")

# ModernGL context
ctx = GL.create_context()

# Create textures and framebuffer
color_texture = ctx.texture((width, height), 4)
depth_texture = ctx.depth_texture((width, height))
size_texture = ctx.texture((width, height), 1)
framebuffer = ctx.framebuffer(color_attachments=[color_texture, size_texture], depth_attachment=depth_texture)

# Particle System Classes
class Particle:
    def __init__(self, position, velocity, size, color, lifespan):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.size = size
        self.color = color
        self.lifespan = lifespan

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifespan -= dt

    def is_alive(self):
        return self.lifespan > 0

class ParticleSystem:
    def __init__(self, max_particles):
        self.particles = []
        self.max_particles = max_particles

    def emit(self, position, velocity, size, color, lifespan):
        if len(self.particles) < self.max_particles:
            self.particles.append(Particle(position, velocity, size, color, lifespan))

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

    def get_data(self):
        positions = []
        sizes = []
        colors = []
        for p in self.particles:
            positions.append(p.position)
            sizes.append(p.size)
            colors.append(p.color)
        return positions, sizes, colors

particle_system = ParticleSystem(max_particles=1000)

def emit_particles():
    for _ in range(10):  # Emit 10 particles per frame
        position = [0.0, 0.0, 0.0]
        velocity = np.random.uniform(-1.0, 1.0, 3)
        size = np.random.uniform(0.1, 1.0)
        color = np.random.uniform(0.0, 1.0, 4)
        lifespan = np.random.uniform(1.0, 5.0)
        particle_system.emit(position, velocity, size, color, lifespan)

# Shaders for rendering particles
vertex_shader_source = """
#version 330 core
layout(location = 0) in vec3 in_position;
layout(location = 1) in float in_size;
layout(location = 2) in vec4 in_color;

out vec4 color;
out float size;

uniform mat4 projection;
uniform mat4 view;

void main() {
    gl_Position = projection * view * vec4(in_position, 1.0);
    color = in_color;
    size = in_size;
}
"""

fragment_shader_source = """
#version 330 core
in vec4 color;
in float size;

layout(location = 0) out vec4 fragColor;
layout(location = 1) out float fragSize;

void main() {
    fragColor = color;
    fragSize = size;
}
"""

program = ctx.program(
    vertex_shader=vertex_shader_source,
    fragment_shader=fragment_shader_source,
)

# Blur shaders
blur_vertex_shader_source = """
#version 330 core
in vec3 in_position;
in vec2 in_uv;
out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 1.0);
    uv = in_uv;
}
"""

blur_fragment_shader_source = """
#version 330 core
in vec2 uv;
out vec4 fragColor;

uniform sampler2D color_texture;
uniform sampler2D depth_texture;
uniform sampler2D size_texture;
uniform float focal_distance;
uniform float blur_scale;

float calculate_blur_radius(float depth, float size) {
    return blur_scale * abs(depth - focal_distance) * size;
}

void main() {
    vec4 color = vec4(0.0);
    float depth = texture(depth_texture, uv).r;
    float size = texture(size_texture, uv).r;
    float blur_radius = calculate_blur_radius(depth, size);

    int samples = int(blur_radius * 10.0);
    float weight_sum = 0.0;
    for (int x = -samples; x <= samples; x++) {
        for (int y = -samples; y <= samples; y++) {
            vec2 offset = vec2(float(x), float(y)) / vec2(textureSize(color_texture, 0));
            float weight = exp(-(dot(offset, offset)) / (2.0 * blur_radius * blur_radius));
            color += texture(color_texture, uv + offset) * weight;
            weight_sum += weight;
        }
    }
    fragColor = color / weight_sum;
}
"""

blur_program = ctx.program(
    vertex_shader=blur_vertex_shader_source,
    fragment_shader=blur_fragment_shader_source,
)

quad_vertices = np.array([
    -1.0, -1.0, 0.0, 0.0, 0.0,
    1.0, -1.0, 0.0, 1.0, 0.0,
    -1.0, 1.0, 0.0, 0.0, 1.0,
    1.0, 1.0, 0.0, 1.0, 1.0,
], dtype='f4')

quad_vbo = ctx.buffer(quad_vertices)
quad_vao = ctx.simple_vertex_array(blur_program, quad_vbo, 'in_position', 'in_uv')

blur_program['focal_distance'].value = 0.5
blur_program['blur_scale'].value = 0.05

# Projection and view matrices
projection_matrix = projection = Matrix44.perspective_projection(45.0, 800 / 600, 0.1, 1000.0)

view = Matrix44.look_at(
    (3.0, 3.0, 3.0),
    (0.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
)

program['projection'].write(projection_matrix.astype('f4'))
program['view'].write(view.astype('f4'))

@window.event
def on_draw():
    window.clear()
    emit_particles()
    particle_system.update(1/75)  # Assume 60 FPS

    positions, sizes, colors = particle_system.get_data()

    if len(positions) == 0:
        return

    particle_data = np.array([
        [*pos, size, *col] for pos, size, col in zip(positions, sizes, colors)
    ], dtype='f4').flatten()

    vbo = ctx.buffer(particle_data)
    vao = ctx.simple_vertex_array(program, vbo, 'in_position', 'in_size', 'in_color')

    framebuffer.use()
    ctx.clear(0.0, 0.0, 0.0, 1.0)
    ctx.enable(GL.DEPTH_TEST)

    vao.render(GL.POINTS)

    color_texture.use(location=0)
    depth_texture.use(location=1)
    size_texture.use(location=2)

    ctx.screen.use()
    quad_vao.render(GL.TRIANGLE_STRIP)
    window.flip()

pyglet.app.run()
