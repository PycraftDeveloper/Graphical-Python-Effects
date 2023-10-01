import pygame
import moderngl
import ctypes
import sys

vertex_shader_sprite = """
#version 330
in vec2 in_position;
in vec2 in_uv;
out vec2 v_uv;
void main()
{
    v_uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

fragment_shader_sprite = """
#version 330
out vec4 fragColor;
uniform sampler2D u_texture;
uniform float y;
in vec2 v_uv;

#define PI 3.1415926535897932384626433832795;

float rand(vec2 c){
	return fract(sin(dot(c.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float noise(vec2 p, float freq ){
	float unit = 1/freq;
	vec2 ij = floor(p/unit);
	vec2 xy = mod(p,unit)/unit;
	xy = 3.*xy*xy-2.*xy*xy*xy;
	//xy = 0.5*(1.-cos(PI*xy));
	float a = rand((ij+vec2(0.,0.)));
	float b = rand((ij+vec2(1.,0.)));
	float c = rand((ij+vec2(0.,1.)));
	float d = rand((ij+vec2(1.,1.)));
	float x1 = mix(a, b, xy.x);
	float x2 = mix(c, d, xy.x);
	return mix(x1, x2, xy.y);
}

float pNoise(vec2 p, int res){
	float persistance = .5;
	float n = 0.;
	float normK = 0.;
	float f = 4.;
	float amp = 1.;
	int iCount = 0;
	for (int i = 0; i<50; i++){
		n+=amp*noise(p, f);
		f*=2.;
		normK+=amp;
		amp*=persistance;
		if (iCount == res) break;
		iCount++;
	}
	float nf = n/normK;
	return nf*nf*nf*nf;
}

void main()
{
    //fragColor = texture(u_texture, v_uv)*pNoise(vec2(v_uv.x, y+v_uv.y), 1);
    vec2 new_v_uv = v_uv*2;
    float transparency = pNoise(vec2(new_v_uv.x, new_v_uv.y+y), 1);
    if (transparency < 0.075) {
        discard;
    } else {
        float y = y/3;
        fragColor = vec4(0.05+pNoise(vec2(y-50, -y+50), 1), 0.05+pNoise(vec2(-y, y), 1), 0.05+pNoise(vec2(y+600, y-750), 1), 1)*(0.9+transparency);
    }
}
"""

class ModernGLGroup(pygame.sprite.Group):

    gl_context = None
    gl_program = None
    gl_buffer = None
    gl_vao = None
    gl_textures = {}
    y = 0

    def __init__(self, sprites = None):
        if sprites == None:
            super().__init__()
        else:
            super().__init__(sprites)

    def get_program():
        if ModernGLGroup.gl_program == None:
            ModernGLGroup.gl_program = ModernGLGroup.gl_context.program(
                vertex_shader = vertex_shader_sprite,
                fragment_shader = fragment_shader_sprite)
        return ModernGLGroup.gl_program

    def get_buffer():
        if ModernGLGroup.gl_buffer == None:
            ModernGLGroup.gl_buffer = ModernGLGroup.gl_context.buffer(None, reserve=6*4*4)
        return ModernGLGroup.gl_buffer

    def get_vao():
        if ModernGLGroup.gl_vao == None:
            ModernGLGroup.gl_vao = ModernGLGroup.gl_context.vertex_array(
                ModernGLGroup.get_program(), [(ModernGLGroup.get_buffer(), "2f4 2f4", "in_position", "in_uv")])
        return ModernGLGroup.gl_vao

    def get_texture(image):
        if not image in ModernGLGroup.gl_textures:
            rgba_image = image.convert_alpha()
            texture = ModernGLGroup.gl_context.texture(rgba_image.get_size(), 4, rgba_image.get_buffer())
            texture.swizzle = 'BGRA'
            ModernGLGroup.gl_textures[image] = texture
        return ModernGLGroup.gl_textures[image]

    def convert_vertex(pt, surface):
        return pt[0] / surface.get_width() * 2 - 1, 1 - pt[1] / surface.get_height() * 2

    def render(sprite, surface):
        corners = [
            ModernGLGroup.convert_vertex(sprite.rect.bottomleft, surface),
            ModernGLGroup.convert_vertex(sprite.rect.bottomright, surface),
            ModernGLGroup.convert_vertex(sprite.rect.topright, surface),
            ModernGLGroup.convert_vertex(sprite.rect.topleft, surface)]

        vertices_quad_2d = (ctypes.c_float * (6*4))(
            *corners[0], 0.0, 1.0,
            *corners[1], 1.0, 1.0,
            *corners[2], 1.0, 0.0,
            *corners[0], 0.0, 1.0,
            *corners[2], 1.0, 0.0,
            *corners[3], 0.0, 0.0)

        ModernGLGroup.get_buffer().write(vertices_quad_2d)
        ModernGLGroup.get_program()["y"] = ModernGLGroup.y
        ModernGLGroup.get_texture(sprite.image).use(0)
        ModernGLGroup.get_vao().render()
        ModernGLGroup.y += 0.001

    def draw(self, surface):
        for sprite in self:
            ModernGLGroup.render(sprite, surface)

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center = (size[0]//2, size[1]//2))

pygame.init()

window = pygame.display.set_mode(
    (1280, 720),
    pygame.DOUBLEBUF|pygame.OPENGL|pygame.HWACCEL,
    vsync=True)
pygame.display.set_caption("Colorful Stacked Patterns - 2")

clock = pygame.time.Clock()

gl_context = moderngl.create_context()
gl_context.enable(moderngl.BLEND)
ModernGLGroup.gl_context = gl_context

sprite_object = SpriteObject(window.get_size())
group = ModernGLGroup(sprite_object)

run = True
fullscreen = False
while 1:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    window = pygame.display.set_mode(
                        (0, 0),
                        pygame.DOUBLEBUF|pygame.OPENGL|pygame.FULLSCREEN|pygame.HWACCEL,
                        vsync=True)
                else:
                    window = pygame.display.set_mode(
                        (1280, 720),
                        pygame.DOUBLEBUF|pygame.OPENGL|pygame.HWACCEL,
                        vsync=True)

                ModernGLGroup.gl_context.viewport = (
                    0,
                    0,
                    *pygame.display.get_window_size())

                sprite_object = SpriteObject(window.get_size())
                group = ModernGLGroup(sprite_object)
                gl_context.clear(0, 0, 0)

    group.draw(window)
    pygame.display.flip()
    clock.tick(200)

pygame.quit()
exit()