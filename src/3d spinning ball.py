import math
import moderngl as mgl
import numpy as np
from PIL import Image
from pyrr import Matrix44
from moderngl_window import geometry, run_window_config
from moderngl_window.conf import settings
from moderngl_window.context.base import WindowConfig
import pmma
from time import perf_counter

pmma.init()

# Set up configuration
class SphereWindow(WindowConfig):
    window_size = (800, 600)
    resource_dir = '.'  # Directory where textures are stored
    aspect_ratio = 800 / 600
    title = "Spinning Textured Sphere"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera_position = (0.0, 0.0, 10.0)  # Move the camera further back
        self.rotation_angle = 0.0

        # Compile shaders
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330 core

            uniform mat4 model;
            uniform mat4 projection;
            uniform sampler2D texture0;

            in vec3 in_position;      // Input vertex position
            in vec2 in_texcoord_0;    // Input texture coordinates

            out float luminance;

            void main() {
                // Sample the texture using the texture coordinates
                vec3 tex_color = texture(texture0, in_texcoord_0).rgb;

                // Calculate the luminance (darker = higher protrusion)
                luminance = 1.0 - dot(tex_color, vec3(0.2126, 0.7152, 0.0722)); // Standard luminance calculation

                // Offset the vertex position along its normal
                vec3 displaced_position = in_position + in_position * luminance * 0.2; // Adjust the 0.2 factor as needed

                // Set the final vertex position
                gl_Position = projection * model * vec4(displaced_position, 1.0);
            }

            """,
            fragment_shader="""
            #version 330 core

            out vec3 fragColor;
            in float luminance;

            uniform vec3 inner_color;
            uniform vec3 outer_color;

            void main() {
                fragColor = mix(inner_color, outer_color, luminance);
            }
            """,
        )

        # Geometry
        self.sphere = geometry.sphere(radius=1.0, sectors=64, rings=64)

        # Uniform locations
        self.model = self.program["model"]
        self.projection = self.program["projection"]

        # Setup projection matrix
        self.projection_matrix = Matrix44.perspective_projection(
            75.0,  # Increase the field of view
            self.aspect_ratio,
            0.1,
            100.0,
        )

        self.texture = self.ctx.texture(
            size=(64, 64),
            components=3,
            data=None,  # No initial data
        )
        self.texture.use(location=0)
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)
        self.texture.repeat_x = True
        self.texture.repeat_y = True

        self.program["inner_color"].write(np.array([1.0, 0.0, 0.0], dtype="f4"))
        self.program["outer_color"].write(np.array([0.0, 0.0, 1.0], dtype="f4"))

        self.noise = pmma.Perlin(octaves=1)
        self.inner_color = pmma.ColorConverter()
        self.outer_color = pmma.ColorConverter()
        pmma.set_in_game_loop(True)

    def render(self, time, frame_time):
        self.ctx.clear(0, 0, 0)
        self.ctx.enable(mgl.DEPTH_TEST)

        # Create texture from integer array
        array = np.zeros((64, 64, 3), dtype=np.uint8)

        for x in range(0, 64):
            for y in range(0, 64):
                c = self.noise.generate_2D_perlin_noise(
    (x % 64) / 20 + time / 5,
    (y % 64) / 20 + time / 5,
    new_range=[0, 255]
)
                array[x][y] = [c, c, c]

        # Resize to fit the sphere's texture size
        rgb_array = array#np.repeat(np.repeat(array, 64 // array.shape[0], axis=0), 64 // array.shape[1], axis=1)

        # Upload texture
        self.texture.write(rgb_array.tobytes())

        # Calculate model matrix
        self.rotation_angle += frame_time/5
        model_matrix = Matrix44.from_translation((0.0, 0.0, -2.0))# * Matrix44.from_eulers((-self.rotation_angle, self.rotation_angle, 0.0))

        # Update uniforms
        self.model.write(model_matrix.astype("f4"))
        self.projection.write(self.projection_matrix.astype("f4"))

        self.program["inner_color"].write(np.array(self.inner_color.generate_color_from_perlin_noise(value=time/10, format=pmma.Constants.SMALL_RGB), dtype="f4"))
        self.program["outer_color"].write(np.array(self.outer_color.generate_color_from_perlin_noise(value=-time/10+20.54365, format=pmma.Constants.SMALL_RGB), dtype="f4"))

        # Render the sphere
        self.sphere.render(self.program)

if __name__ == "__main__":
    settings.WINDOW['class'] = 'pyglet'
    run_window_config(SphereWindow)
