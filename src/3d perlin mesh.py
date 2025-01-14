import moderngl
from moderngl_window import WindowConfig, run_window_config
from moderngl_window.geometry import sphere
from pyrr import Matrix44, Vector3
import numpy as np
import pmma

pmma.init()

noise = pmma.Perlin()
color = pmma.ColorConverter()

class SphereGrid(WindowConfig):
    title = "3D Sphere Grid"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resource_dir = "."

    # Grid size
    GRID_SIZE = 20
    SPHERE_SCALE = 0.3  # Adjust to scale the spheres
    GRID_SPACING = 3  # Space between spheres

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            in vec3 in_position;
            in vec3 in_normal;
            out vec3 normal;

            void main() {
                gl_Position = projection * view * model * vec4(in_position, 1.0);
                normal = in_normal;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 normal;
            out vec4 fragColor;
            uniform vec3 top_shape_color;
            uniform vec3 bottom_shape_color;
            uniform float y_value;

            float max_value = 10;

            void main() {
                fragColor = vec4(mix(top_shape_color, bottom_shape_color, y_value/max_value), 1.0);
            }
            """
        )

        # Create a sphere geometry object
        self.sphere = sphere(radius=1.0, sectors=32, rings=32)
        self.camera_distance = 20.0
        self.camera_angle = 0.0

        # Store grid positions
        self.grid_positions = [
            [
                Vector3([
                    (i - self.GRID_SIZE / 2) * self.GRID_SPACING,
                    0.0,
                    (j - self.GRID_SIZE / 2) * self.GRID_SPACING
                ])
                for j in range(self.GRID_SIZE)
            ]
            for i in range(self.GRID_SIZE)
        ]

    def render(self, time, frametime):
        self.ctx.clear(0, 0, 0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Create a rotating camera
        self.camera_angle += frametime
        cam_x = self.camera_distance * np.sin(self.camera_angle)
        cam_z = self.camera_distance * np.cos(self.camera_angle)
        camera_position = Vector3([cam_x, self.camera_distance * 0.5, cam_z])
        look_at = Vector3([0.0, 0.0, 0.0])
        up = Vector3([0.0, 1.0, 0.0])

        view = Matrix44.look_at(camera_position, look_at, up)
        projection = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)

        self.prog["view"].write(view.astype("f4"))
        self.prog["projection"].write(projection.astype("f4"))

        self.prog["top_shape_color"] = color.generate_color_from_perlin_noise(value=pmma.get_application_run_time()/5, format=pmma.Constants.SMALL_RGB)  # Set the color of the spheres
        self.prog["bottom_shape_color"] = color.generate_color_from_perlin_noise(value=-pmma.get_application_run_time()/5, format=pmma.Constants.SMALL_RGB)  # Set the color of the spheres

        # Draw the grid of spheres
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                x, y, z = self.grid_positions[i][j]
                # Example: make spheres bounce in a sine wave
                self.grid_positions[i][j] = Vector3([
                    x,
                    noise.generate_2D_perlin_noise(x=(x / 25)+pmma.get_application_run_time(), y=(z / 25)+pmma.get_application_run_time(), new_range=[0, 10]),
                    z])

                self.prog["y_value"] = self.grid_positions[i][j].y

                position = self.grid_positions[i][j]
                model = Matrix44.from_translation(position) @ Matrix44.from_scale(
                    [self.SPHERE_SCALE] * 3
                )
                self.prog["model"].write(model.astype("f4"))
                self.sphere.render(self.prog)


if __name__ == "__main__":
    run_window_config(SphereGrid)
