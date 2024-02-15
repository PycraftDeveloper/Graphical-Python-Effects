import ctypes
import sys
import random
from math import floor
from ctypes import c_int64
import time
from os import sep

import pygame
import moderngl
from PIL import Image

import numpy as np
import numba

GRADIENTS2 = np.array([
    5, 2, 2, 5,
    -5, 2, -2, 5,
    5, -2, 2, -5,
    -5, -2, -2, -5,
], dtype=np.int64)

GRADIENTS3 = np.array([
    -11, 4, 4, -4, 11, 4, -4, 4, 11,
    11, 4, 4, 4, 11, 4, 4, 4, 11,
    -11, -4, 4, -4, -11, 4, -4, -4, 11,
    11, -4, 4, 4, -11, 4, 4, -4, 11,
    -11, 4, -4, -4, 11, -4, -4, 4, -11,
    11, 4, -4, 4, 11, -4, 4, 4, -11,
    -11, -4, -4, -4, -11, -4, -4, -4, -11,
    11, -4, -4, 4, -11, -4, 4, -4, -11,
], dtype=np.int64)

GRADIENTS4 = np.array([
    3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3,
    -3, 1, 1, 1, -1, 3, 1, 1, -1, 1, 3, 1, -1, 1, 1, 3,
    3, -1, 1, 1, 1, -3, 1, 1, 1, -1, 3, 1, 1, -1, 1, 3,
    -3, -1, 1, 1, -1, -3, 1, 1, -1, -1, 3, 1, -1, -1, 1, 3,
    3, 1, -1, 1, 1, 3, -1, 1, 1, 1, -3, 1, 1, 1, -1, 3,
    -3, 1, -1, 1, -1, 3, -1, 1, -1, 1, -3, 1, -1, 1, -1, 3,
    3, -1, -1, 1, 1, -3, -1, 1, 1, -1, -3, 1, 1, -1, -1, 3,
    -3, -1, -1, 1, -1, -3, -1, 1, -1, -1, -3, 1, -1, -1, -1, 3,
    3, 1, 1, -1, 1, 3, 1, -1, 1, 1, 3, -1, 1, 1, 1, -3,
    -3, 1, 1, -1, -1, 3, 1, -1, -1, 1, 3, -1, -1, 1, 1, -3,
    3, -1, 1, -1, 1, -3, 1, -1, 1, -1, 3, -1, 1, -1, 1, -3,
    -3, -1, 1, -1, -1, -3, 1, -1, -1, -1, 3, -1, -1, -1, 1, -3,
    3, 1, -1, -1, 1, 3, -1, -1, 1, 1, -3, -1, 1, 1, -1, -3,
    -3, 1, -1, -1, -1, 3, -1, -1, -1, 1, -3, -1, -1, 1, -1, -3,
    3, -1, -1, -1, 1, -3, -1, -1, 1, -1, -3, -1, 1, -1, -1, -3,
    -3, -1, -1, -1, -1, -3, -1, -1, -1, -1, -3, -1, -1, -1, -1, -3,
], dtype=np.int64)

STRETCH_CONSTANT2 = -0.211324865405187
SQUISH_CONSTANT2 = 0.366025403784439
STRETCH_CONSTANT3 = -1.0 / 6
SQUISH_CONSTANT3 = 1.0 / 3
STRETCH_CONSTANT4 = -0.138196601125011
SQUISH_CONSTANT4 = 0.309016994374947

NORM_CONSTANT2 = 47
NORM_CONSTANT3 = 103
NORM_CONSTANT4 = 30

@numba.njit()
def extrapolate2(perm, xsb, ysb, dx, dy):
    index = perm[(perm[xsb & 0xFF] + ysb) & 0xFF] & 0x0E
    g1, g2 = GRADIENTS2[index : index + 2]
    return g1 * dx + g2 * dy

@numba.njit()
def generatekey(x, y, perm):
    stretch_offset = (x + y) * STRETCH_CONSTANT2

    xs = x + stretch_offset
    ys = y + stretch_offset

    xsb = floor(xs)
    ysb = floor(ys)

    squish_offset = (xsb + ysb) * SQUISH_CONSTANT2
    xb = xsb + squish_offset
    yb = ysb + squish_offset

    xins = xs - xsb
    yins = ys - ysb

    in_sum = xins + yins

    dx0 = x - xb
    dy0 = y - yb

    value = 0

    dx1 = dx0 - 1 - SQUISH_CONSTANT2
    dy1 = dy0 - 0 - SQUISH_CONSTANT2
    attn1 = 2 - dx1 * dx1 - dy1 * dy1
    if attn1 > 0:
        attn1 *= attn1
        value += attn1 * attn1 * extrapolate2(perm, xsb + 1, ysb + 0, dx1, dy1)

    dx2 = dx0 - 0 - SQUISH_CONSTANT2
    dy2 = dy0 - 1 - SQUISH_CONSTANT2
    attn2 = 2 - dx2 * dx2 - dy2 * dy2
    if attn2 > 0:
        attn2 *= attn2
        value += attn2 * attn2 * extrapolate2(perm, xsb + 0, ysb + 1, dx2, dy2)

    if in_sum <= 1:
        zins = 1 - in_sum
        if zins > xins or zins > yins:
            if xins > yins:
                xsv_ext = xsb + 1
                ysv_ext = ysb - 1
                dx_ext = dx0 - 1
                dy_ext = dy0 + 1
            else:
                xsv_ext = xsb - 1
                ysv_ext = ysb + 1
                dx_ext = dx0 + 1
                dy_ext = dy0 - 1
        else:
            xsv_ext = xsb + 1
            ysv_ext = ysb + 1
            dx_ext = dx0 - 1 - 2 * SQUISH_CONSTANT2
            dy_ext = dy0 - 1 - 2 * SQUISH_CONSTANT2
    else:
        zins = 2 - in_sum
        if zins < xins or zins < yins:
            if xins > yins:
                xsv_ext = xsb + 2
                ysv_ext = ysb + 0
                dx_ext = dx0 - 2 - 2 * SQUISH_CONSTANT2
                dy_ext = dy0 + 0 - 2 * SQUISH_CONSTANT2
            else:
                xsv_ext = xsb + 0
                ysv_ext = ysb + 2
                dx_ext = dx0 + 0 - 2 * SQUISH_CONSTANT2
                dy_ext = dy0 - 2 - 2 * SQUISH_CONSTANT2
        else:
            dx_ext = dx0
            dy_ext = dy0
            xsv_ext = xsb
            ysv_ext = ysb
        xsb += 1
        ysb += 1
        dx0 = dx0 - 1 - 2 * SQUISH_CONSTANT2
        dy0 = dy0 - 1 - 2 * SQUISH_CONSTANT2

    attn0 = 2 - dx0 * dx0 - dy0 * dy0
    if attn0 > 0:
        attn0 *= attn0
        value += attn0 * attn0 * extrapolate2(perm, xsb, ysb, dx0, dy0)

    attn_ext = 2 - dx_ext * dx_ext - dy_ext * dy_ext
    if attn_ext > 0:
        attn_ext *= attn_ext
        value += attn_ext * attn_ext * extrapolate2(perm, xsv_ext, ysv_ext, dx_ext, dy_ext)

    return value / NORM_CONSTANT2

def overflow(x):
    return c_int64(x).value

def getseed(seed):
    perm = np.zeros(256, dtype=np.int64)
    perm_grad_index3 = np.zeros(256, dtype=np.int64)
    source = np.arange(256)

    seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    for i in range(255, -1, -1):
        seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
        r = int((seed + 31) % (i + 1))
        if r < 0:
            r += i + 1
        perm[i] = source[r]

        perm_grad_index3[i] = int((perm[i] % (len(GRADIENTS3) / 3)) * 3)
        source[r] = source[i]

    return perm

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
uniform vec3 color;
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
    if (transparency < 0.085) {
        discard;
    } else {
        float y = y/3;
        fragColor = vec4(color, 1)*(0.9+transparency);
    }
}
"""
# def 0.075
# larger means less solid
# smaller means more solid
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

    def render(sprite, surface, color):
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
        ModernGLGroup.get_program()["color"] = color
        ModernGLGroup.get_texture(sprite.image).use(0)
        ModernGLGroup.get_vao().render()
        ModernGLGroup.y += 0.001

    def draw(self, surface, color):
        for sprite in self:
            ModernGLGroup.render(sprite, surface, color)

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center = (size[0]//2, size[1]//2))

pygame.init()

window = pygame.display.set_mode(
    (0, 0),
    pygame.DOUBLEBUF|pygame.OPENGL|pygame.FULLSCREEN|pygame.HWACCEL)
pygame.display.set_caption("Colorful Stacked Patterns - 3")

clock = pygame.time.Clock()

gl_context = moderngl.create_context()
gl_context.enable(moderngl.BLEND)
ModernGLGroup.gl_context = gl_context

sprite_object = SpriteObject(window.get_size())
group = ModernGLGroup(sprite_object)

rseed = getseed(random.randint(0, 99999))
gseed = getseed(random.randint(0, 99999))
bseed = getseed(random.randint(0, 99999))

run = True
fullscreen = False
now_time = 0
do_now_time = True
while 1:
    start = time.perf_counter()
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_LEFT:
                now_time -= 5
                if now_time < 0:
                    now_time = 0
            elif event.key == pygame.K_RIGHT:
                now_time += 5
            elif event.key == pygame.K_SPACE:
                do_now_time = not do_now_time

            elif event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    window = pygame.display.set_mode(
                        (0, 0),
                        pygame.DOUBLEBUF|pygame.OPENGL|pygame.FULLSCREEN|pygame.HWACCEL)
                else:
                    window = pygame.display.set_mode(
                        (1280, 720),
                        pygame.DOUBLEBUF|pygame.OPENGL|pygame.HWACCEL)

                ModernGLGroup.gl_context.viewport = (
                    0,
                    0,
                    *pygame.display.get_window_size())

                sprite_object = SpriteObject(window.get_size())
                group = ModernGLGroup(sprite_object)
                gl_context.clear(0, 0, 0)

    c1 = generatekey(now_time/50, 0, rseed)
    c2 = generatekey(now_time/50, 0, gseed)
    c3 = generatekey(now_time/50, 0, bseed)

    if do_now_time:
        group.draw(window, (c1, c2, c3))
    pygame.display.flip()
    clock.tick(60) # 200
    if do_now_time:
        now_time += time.perf_counter()-start

pygame.quit()
exit()