import pygame
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
import pmma
import time

pmma.init()

class Ring:
    def __init__(self, ctx, index, inner_radius=0.3, outer_radius=0.5, segments=64, rings=32):
        """Creates a 3D ring with smooth shading."""
        self.ctx = ctx
        self.outer_radius = outer_radius
        self.program = self.create_shader()

        # Generate torus vertices, normals, and indices
        self.vbo, self.ibo, self.num_indices = self.generate_torus(inner_radius, outer_radius, segments, rings)

        # Create a VAO (Vertex Array Object)
        self.vao = self.ctx.vertex_array(
            self.program, [(self.vbo, '3f 3f', 'in_position', 'in_normal')], self.ibo
        )
        self.color = pmma.ColorConverter()
        self.start = time.perf_counter()
        self.index = (index * 50) / 300

    def create_shader(self):
        """Creates the shader program for smooth shading."""
        return self.ctx.program(
            vertex_shader="""
            #version 330
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            uniform float scale;
            in vec3 in_position;
            in vec3 in_normal;
            out vec3 frag_normal;
            void main() {
                frag_normal = normalize(mat3(model) * in_normal);
                gl_Position = projection * view * model * vec4(in_position * scale, 1.0);
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 frag_normal;
            out vec4 fragColor;
            uniform vec3 u_color;
            void main() {
                vec3 normal = gl_FrontFacing ? frag_normal : -frag_normal; // Flip normal for back-faces
                float light = dot(normalize(normal), vec3(0.0, 0.0, 1.0)) * 0.5 + 0.5;
                fragColor = vec4(u_color.rgb, 1.0) * light;
            }
            """
        )

    def generate_torus(self, inner_radius, outer_radius, segments, rings):
        """Generates torus (ring) vertices, normals, and indices."""
        vertices = []
        indices = []

        for i in range(rings):
            theta = i * 2 * np.pi / rings
            cos_theta, sin_theta = np.cos(theta), np.sin(theta)

            for j in range(segments):
                phi = j * 2 * np.pi / segments
                cos_phi, sin_phi = np.cos(phi), np.sin(phi)

                # Vertex position
                x = (outer_radius + inner_radius * cos_phi) * cos_theta
                y = (outer_radius + inner_radius * cos_phi) * sin_theta
                z = inner_radius * sin_phi

                # Normal vector
                nx = cos_phi * cos_theta
                ny = cos_phi * sin_theta
                nz = sin_phi

                vertices.extend([x, y, z, nx, ny, nz])

        for i in range(rings):
            for j in range(segments):
                next_i = (i + 1) % rings
                next_j = (j + 1) % segments

                indices.extend([
                    i * segments + j, next_i * segments + j, i * segments + next_j,
                    next_i * segments + j, next_i * segments + next_j, i * segments + next_j
                ])

        vbo = self.ctx.buffer(np.array(vertices, dtype='f4'))
        ibo = self.ctx.buffer(np.array(indices, dtype='i4'))

        return vbo, ibo, len(indices)

    def render(self, projection_matrix, view_matrix, rotation):
        """Renders the ring with smooth shading."""
        self.program['model'].write(rotation.astype('f4'))
        self.program['view'].write(view_matrix.astype('f4'))
        self.program['projection'].write(projection_matrix.astype('f4'))
        self.program['u_color'].write(self.color.generate_color_from_perlin_noise(time.perf_counter() - self.start, format=pmma.Constants.SMALL_RGB))
        self.program['scale'] = self.index
        self.vao.render(moderngl.TRIANGLES)


class Renderer:
    def __init__(self, width=1920, height=1080):
        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        self.ctx = moderngl.create_context()
        self.clock = pygame.time.Clock()
        self.width, self.height = width, height

        # Create multiple smooth ring instances
        # Generate 100 concentric rings
        self.rings = [
            Ring(self.ctx, i, inner_radius=1, outer_radius=2) for i in range(10)
        ]


        # Determine largest ring radius
        self.max_radius = max(ring.outer_radius for ring in self.rings)

        # Camera setup
        self.setup_camera()

        self.ctx.enable(moderngl.CULL_FACE)  # Hide inside faces
        self.ctx.front_face = 'ccw'  # Ensure correct front-face
        self.ctx.enable(moderngl.DEPTH_TEST)  # Fix depth sorting issues

    def setup_camera(self):
        """Set up the projection and view matrices to focus on the rings."""
        fov = 45  # Field of View
        aspect_ratio = self.width / self.height
        near_plane = 0.001
        far_plane = 1000.0

        # Projection matrix (Perspective)
        self.projection = Matrix44.perspective_projection(fov, aspect_ratio, near_plane, far_plane)

        # Camera position: Distance should be enough to see the largest ring
        camera_distance = 15#self.rings[-1].outer_radius * 2.5
        self.camera_position = Vector3([0.0, 0.0, camera_distance])

        # View matrix: Looking at the center from `camera_position`
        self.view = Matrix44.look_at(
            eye=self.camera_position,    # Camera position
            target=Vector3([0.0, 0.0, 0.0]),  # Looking at the origin
            up=Vector3([0.0, 1.0, 0.0])  # Up direction
        )

    def run(self):
        """Main render loop."""
        angle = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.ctx.clear(0.1, 0.1, 0.1)

            # Rotate rings
            angle += 1
            index = 0
            for ring in self.rings:
                rotation = Matrix44.from_eulers((index + (angle * np.pi / 180), index + (angle * np.pi / 180), index + (angle * np.pi / 180)))
                ring.render(self.projection, self.view, rotation)
                index += 0# 0.1

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    Renderer().run()
