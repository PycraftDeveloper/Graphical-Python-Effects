import random
from math import floor
from ctypes import c_int64

import numpy as np
import pygame
import numba
from pygame import gfxdraw

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

@numba.njit(cache=True)
def extrapolate2(perm, xsb, ysb, dx, dy):
    index = perm[(perm[xsb & 0xFF] + ysb) & 0xFF] & 0x0E
    g1, g2 = GRADIENTS2[index : index + 2]
    return g1 * dx + g2 * dy

@numba.njit(cache=True)
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

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN, vsync=1)

clock = pygame.time.Clock()

seed = getseed(random.randint(0, 100000))
seedr = getseed(random.randint(0, 100000))
seedg = getseed(random.randint(0, 100000))
seedb = getseed(random.randint(0, 100000))

x = 0
while True:
    window_size = display.get_width(), display.get_height()

    Surface = pygame.Surface(window_size).convert()
    Surface.fill((0, 0, 0))

    Surface.set_colorkey((0, 0, 0))
    Surface2 = pygame.Surface(window_size)

    Surface2.fill((0, 0, 0))
    #display.fill([0, 0, 0])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

    color = [
        (1+generatekey(x/100, 0, seedr))*127.5,
        (1+generatekey(x/100, 0, seedg))*127.5,
        (1+generatekey(x/100, 0, seedb))*127.5]

    for row in range(0, display.get_width(), 8):
        for column in range(0, display.get_height(), 8):
            r = row + 64*generatekey((row+x)/500, column/500, seed)
            c = column + 64*generatekey(row/500, (column+x)/500, seed)
            gfxdraw.pixel(Surface, int(r), int(c), color)

    x += 1

    Surface2.set_alpha(1) # 10

    display.blit(Surface2, (0, 0))

    display.blit(Surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)