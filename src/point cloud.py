import pygame
import moderngl
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL, FULLSCREEN
import pmma
import time

pmma.init()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), DOUBLEBUF | OPENGL | FULLSCREEN)
clock = pygame.time.Clock()

# Initialize ModernGL
ctx = moderngl.create_context()

# Create a simple shader program
vertex_shader = '''
    #version 330
    uniform mat4 model;
    uniform mat4 projection;
    uniform mat4 view;

    in vec3 in_position;
    in vec3 in_color;
    in float in_point_size;

    out vec3 color;

    void main() {
        gl_Position = projection * view * vec4(in_position, 1.0);
        color = in_color;
        gl_PointSize = in_point_size;  // Set point size here
    }
'''

fragment_shader = '''
    #version 330
    in vec3 color;
    out vec4 fragColor;

    void main() {
        fragColor = vec4(color, 1.0);
    }
'''

prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

# Create a projection matrix (Perspective)
proj = np.identity(4, dtype='f4')
fov = 45
aspect_ratio = screen.get_width() / screen.get_height()
near = 0.1
far = 100.0
proj[0, 0] = 1 / (aspect_ratio * np.tan(np.radians(fov) / 2))
proj[1, 1] = 1 / np.tan(np.radians(fov) / 2)
proj[2, 2] = -(far + near) / (far - near)
proj[2, 3] = -1
proj[3, 2] = -(2 * far * near) / (far - near)
proj[3, 3] = 0
prog['projection'].write(proj.tobytes())

# Create a view matrix (Camera)
view = np.identity(4, dtype='f4')
view[3, 2] = -5.0  # Move camera back
prog['view'].write(view.tobytes())

class Point:
    def __init__(self, position, color, point_size):
        self.position = np.array(position, dtype='f4')
        self.color = np.array(color, dtype='f4')
        self.point_size = np.array([point_size], dtype='f4')
        self.x_noise = pmma.Perlin()
        self.y_noise = pmma.Perlin()
        self.z_noise = pmma.Perlin()

    def update_position(self):
        position = [
            self.x_noise.generate_1D_perlin_noise(now_time/5, new_range=[-2*aspect_ratio, 2*aspect_ratio]),
            3,#self.y_noise.generate_1D_perlin_noise(now_time/100, new_range=[5, 20]),
            self.z_noise.generate_1D_perlin_noise(-now_time/5, new_range=[-2, 2])
        ]
        _position = [position[0], position[2]]
        self.position = np.array(_position, dtype='f4')
        self.point_size = np.array([position[1]], dtype='f4')

# Generate random points
num_points = 100#00
points = [
    Point(
        position=np.random.uniform(-5, 5, 3),
        color=np.random.uniform(0, 1, 3),
        point_size=np.random.uniform(1.0, 5.0)
    )
    for _ in range(num_points)
]

# Extract positions, colors, and point sizes
positions = np.array([point.position for point in points], dtype='f4').flatten()
colors = np.array([point.color for point in points], dtype='f4').flatten()
point_sizes = np.array([point.point_size for point in points], dtype='f4').flatten()

# Create buffer objects
vbo_positions = ctx.buffer(positions.tobytes())
vbo_colors = ctx.buffer(colors.tobytes())
vbo_point_sizes = ctx.buffer(point_sizes.tobytes())

# Create vertex array object
vao = ctx.vertex_array(prog, [
    (vbo_positions, '3f', 'in_position'),
    (vbo_colors, '3f', 'in_color'),
    (vbo_point_sizes, '1f', 'in_point_size'),
])

ctx.enable(moderngl.PROGRAM_POINT_SIZE)
# Main loop
running = True
start = time.perf_counter()
now_time = 0
pmma.Registry.in_game_loop = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update positions to make points move (simple random walk)
    for point in points:
        point.update_position()
        #point.position += np.random.uniform(-0.01, 0.01, point.position.shape).astype('f4')

    # Update VBO data
    vbo_positions.write(np.array([point.position for point in points], dtype='f4').flatten().tobytes())
    vbo_point_sizes.write(np.array([point.point_size for point in points], dtype='f4').flatten().tobytes())

    # Clear the screen
    ctx.clear()

    # Render the points
    vao.render(moderngl.POINTS)

    # Swap buffers
    pygame.display.flip()
    clock.tick(60)
    now_time = time.perf_counter() - start

# Clean up
pygame.quit()
