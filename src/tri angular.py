import numpy as np
import moderngl
import moderngl_window as mglw

import pmma

pmma.init()

top_left_color = pmma.ColorConverter()
top_right_color = pmma.ColorConverter()
bottom_left_color = pmma.ColorConverter()
bottom_right_color = pmma.ColorConverter()

class ModernglLogo(mglw.WindowConfig):
    title = "ModernGL Logo"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 vert;
                in vec4 vert_color;

                out vec4 frag_color;

                void main() {
                    frag_color = vert_color;
                    gl_Position = vec4(vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                in vec4 frag_color;
                out vec4 color;

                void main() {
                    color = frag_color;
                }
            ''',
        )

    def render(self, time, frametime):
        color_for_top_left = top_left_color.generate_color_from_perlin_noise(50.91+time/5, format=pmma.Constants.SMALL_RGB)
        color_for_top_right = top_right_color.generate_color_from_perlin_noise(time/5, format=pmma.Constants.SMALL_RGB)
        color_for_bottom_left = bottom_left_color.generate_color_from_perlin_noise(90.173+time/5, format=pmma.Constants.SMALL_RGB)
        color_for_bottom_right = bottom_right_color.generate_color_from_perlin_noise(38.75+time/5, format=pmma.Constants.SMALL_RGB)
        # Define two triangles to form a rectangle
        vertices = np.array([
            # First triangle
            -1.0,  1.0,  *color_for_top_left, 1.0,  # Top-left corner (Red)
             1.0,  1.0,  *color_for_top_right, 1.0,  # Top-right corner (Green)
            -1.0, -1.0,  *color_for_bottom_left, 1.0,  # Bottom-left corner (Blue)

            # Second triangle
             1.0,  1.0,  *color_for_top_right, 1.0,  # Top-right corner (Red)
             1.0, -1.0,  *color_for_bottom_right, 1.0,  # Bottom-right corner (Purple)
            -1.0, -1.0,  *color_for_bottom_left, 1.0,  # Bottom-left corner (Blue)
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'vert', 'vert_color')

        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.BLEND)
        self.vao.render(moderngl.TRIANGLES)

if __name__ == '__main__':
    mglw.run_window_config(ModernglLogo)
