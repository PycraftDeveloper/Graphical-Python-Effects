import pygame
import moderngl
import numpy as np
import math

# Recursive function to create the Menger Sponge vertices and indices
def generate_menger_sponge(level, size):
    if level == 0:
        half_size = size / 2.0
        vertices = [
            [-half_size, -half_size, -half_size],  # Bottom-left-back
            [ half_size, -half_size, -half_size],  # Bottom-right-back
            [ half_size,  half_size, -half_size],  # Top-right-back
            [-half_size,  half_size, -half_size],  # Top-left-back
            [-half_size, -half_size,  half_size],  # Bottom-left-front
            [ half_size, -half_size,  half_size],  # Bottom-right-front
            [ half_size,  half_size,  half_size],  # Top-right-front
            [-half_size,  half_size,  half_size]   # Top-left-front
        ]
        # Cube faces
        indices = [
            [0, 1, 2, 3],  # Back face
            [4, 5, 6, 7],  # Front face
            [0, 1, 5, 4],  # Bottom face
            [3, 2, 6, 7],  # Top face
            [0, 3, 7, 4],  # Left face
            [1, 2, 6, 5]   # Right face
        ]
        return vertices, indices
    else:
        sub_size = size / 3.0
        vertices = []
        indices = []
        sub_vertices, sub_indices = generate_menger_sponge(level - 1, sub_size)

        # Create the sponge pattern
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    if (x == 1 and y == 1) or (x == 1 and z == 1) or (y == 1 and z == 1):
                        continue
                    offset = [(x - 1) * sub_size, (y - 1) * sub_size, (z - 1) * sub_size]
                    for v in sub_vertices:
                        vertices.append([v[i] + offset[i] for i in range(3)])
                    base_index = len(vertices) - len(sub_vertices)
                    for face in sub_indices:
                        indices.append([base_index + i for i in face])
        return vertices, indices

def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    screen = pygame.display.set_mode((1920, 1080), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    ctx = moderngl.create_context()

    # Generate initial Menger Sponge data
    level = 4  # Start with level 1
    vertices, indices = generate_menger_sponge(level, 1.0)

    # Flatten the vertex and index data
    vertex_data = np.array(vertices, dtype='f4').flatten()
    index_data = np.array(indices, dtype='i4').flatten()

    # Vertex shader
    vertex_shader = '''
    #version 330
    in vec3 in_position;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    out vec3 frag_color;
    void main() {
        frag_color = vec3(1.0, 0.5, 0.3);  // Base color
        gl_Position = projection * view * model * vec4(in_position, 1.0);
    }
    '''

    # Fragment shader
    fragment_shader = '''
    #version 330
    in vec3 frag_color;
    out vec4 out_color;
    void main() {
        out_color = vec4(frag_color, 1.0);
    }
    '''

    program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    # Buffers
    vbo = ctx.buffer(vertex_data)
    ibo = ctx.buffer(index_data)

    vao = ctx.vertex_array(program, [
        (vbo, '3f', 'in_position')
    ], ibo)

    # Matrices
    projection = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, -2 / (10 - 0.1), - (10 + 0.1) / (10 - 0.1)],
        [0, 0, 0, 1]
    ], dtype='f4')

    angle_x = 0
    angle_y = 0
    zoom = -1

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP and level < 4:
                    level += 1
                    vertices, indices = generate_menger_sponge(level, 1.0)
                    vertex_data = np.array(vertices, dtype='f4').flatten()
                    index_data = np.array(indices, dtype='i4').flatten()
                    vbo.write(vertex_data)
                    ibo.write(index_data)
                elif event.key == pygame.K_DOWN and level > 0:
                    level -= 1
                    vertices, indices = generate_menger_sponge(level, 1.0)
                    vertex_data = np.array(vertices, dtype='f4').flatten()
                    index_data = np.array(indices, dtype='i4').flatten()
                    vbo.write(vertex_data)
                    ibo.write(index_data)

        # Update angle for rotation
        angle_x += 0.001
        angle_y += 0.001

        # Model matrix
        model = np.array([
            [math.cos(angle_y), 0, math.sin(angle_y), 0],
            [0, 1, 0, 0],
            [-math.sin(angle_y), 0, math.cos(angle_y), 0],
            [0, 0, -zoom, 1]
        ], dtype='f4')

        view = np.identity(4, dtype='f4')

        ctx.clear(0.1, 0.1, 0.1)
        ctx.enable(moderngl.DEPTH_TEST)

        program['model'].write(model.tobytes())
        program['view'].write(view.tobytes())
        program['projection'].write(projection.tobytes())

        vao.render(moderngl.POINTS)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
