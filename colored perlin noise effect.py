import pygame
import random

import numpy as np
from math import floor
from ctypes import c_int64
import random

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

@numba.njit(fastmath=True, parallel=True)
def extrapolate2(perm, xsb, ysb, dx, dy):
    index = perm[(perm[xsb & 0xFF] + ysb) & 0xFF] & 0x0E
    g1, g2 = GRADIENTS2[index : index + 2]
    return g1 * dx + g2 * dy

@numba.njit(fastmath=True, parallel=True)
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

pygame.init()

def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(),
        pilImage.size,
        pilImage.mode)

def gradientRect( window, left_colour, right_colour, target_rect, c7 ):
    """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
    colour_rect = pygame.Surface( ( 2, 2 ) )                                   # tiny! 2x2 bitmap
    pygame.draw.line( colour_rect, left_colour,  ( 0,0 ), ( 0,1 ) )            # left colour line
    pygame.draw.line( colour_rect, right_colour, ( 1,0 ), ( 1,1 ) )            # right colour line
    colour_rect = pygame.transform.smoothscale( colour_rect, ( target_rect.width, target_rect.height ) )  # stretch!
    new_rect = pygame.transform.rotate(colour_rect, c7)
    window.blit( new_rect, target_rect )  

clock = pygame.time.Clock()

pygame.display.set_caption("Its EASTER!!!!")

i = 0

c1_seed = getseed(int(random.random()*200))
c2_seed = getseed(int(random.random()*200))
c3_seed = getseed(int(random.random()*200))

c4_seed = getseed(int(random.random()*200))
c5_seed = getseed(int(random.random()*200))
c6_seed = getseed(int(random.random()*200))

c7_seed = getseed(int(random.random()*200))

c8_seed = getseed(int(random.random()*200))
c9_seed = getseed(int(random.random()*200))

c1, c2, c3 = generatekey(i, 0, c1_seed), generatekey(i, 0, c2_seed), generatekey(i, 0, c3_seed)
c4, c5, c6 = generatekey(i, 0, c4_seed), generatekey(i, 0, c5_seed), generatekey(i, 0, c6_seed)

flags = pygame.DOUBLEBUF | pygame.FULLSCREEN
display = pygame.display.set_mode((1920, 1080), flags, 16)

c7 = generatekey(i, 0, c7_seed)
while True:
    #gradientRect(display, [int(c1), int(c2), int(c3)], [int(c4), int(c5), int(c6)], rect, c7)
    pygame.display.set_caption(f"Its EASTER!!!! {clock.get_fps()}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

    c1 += generatekey(i, 0, c1_seed)*random.random()*5
    c2 += generatekey(i, 0, c2_seed)*random.random()*5
    c3 += generatekey(i, 0, c3_seed)*random.random()*5

    '''c4 += generatekey(i, 0, c4_seed)*random.random()*5
    c5 += generatekey(i, 0, c5_seed)*random.random()*5
    c6 += generatekey(i, 0, c6_seed)*random.random()*5

    c7 += generatekey(i, 0, c7_seed)*random.random()*5'''

    if c1 > 255:
        c1 = 255
    elif c1 < 100:
        c1 = 100

    if c2 > 255:
        c2 = 255
    elif c2 < 0:
        c2 = 0

    if c3 > 255:
        c3 = 255
    elif c3 < 0:
        c3 = 0

    if c4 > 255:
        c4 = 255
    elif c4 < 100:
        c4 = 100

    if c5 > 255:
        c5 = 255
    elif c5 < 0:
        c5 = 0

    if c6 > 255:
        c6 = 255
    elif c6 < 0:
        c6 = 0

    res = 8
    for x in range(int(display.get_width()/res)):
        for y in range(int(display.get_height()/res)):
            g = generatekey(x/30, y/30+i, c8_seed)
            if g > 0:
                size = res
                rect = pygame.Rect(x*size-size/2, y*size-size/2, size, size)
                cq_1 = int(c1/(1-g))
                cq_2 = int(c2/(1-g))
                cq_3 = int(c3/(1-g))

                if cq_1 > 255:
                    cq_1 = 255
                elif cq_1 < 0:
                    cq_1 = 0

                if cq_2 > 255:
                    cq_2 = 255
                elif cq_2 < 0:
                    cq_2 = 0

                if cq_3 > 255:
                    cq_3 = 255
                elif cq_3 < 0:
                    cq_3 = 0
                bdr = 0
                pygame.draw.rect(display, [cq_1, cq_2, cq_3], rect, border_radius=bdr)

    #display.blit(image, (0, 0))

    pygame.display.flip()
    clock.tick(60)
    i += 0.007 #0.002