import pygame
import pmma
import random
import time

pygame.init()
pmma.init()

display = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

SQUARE_SIZE = 20
SQUARE_SPACER = 5
SQUARE_COUNT = display.get_height() // (SQUARE_SIZE + SQUARE_SPACER)
SQUARE_X_CENTER = (display.get_width() - SQUARE_SIZE) // 2
SQUARE_Y_OFFSET = (display.get_height() % (SQUARE_SIZE + SQUARE_SPACER))/2
ANIMATION_DURATION = 3

def apply_color_offset(value, offset):
    red = value[0] + offset[0]
    green = value[1] + offset[1]
    blue = value[2] + offset[2]
    if red > 255: red = 255
    if green > 255: green = 255
    if blue > 255: blue = 255
    if red < 0: red = 0
    if green < 0: green = 0
    if blue < 0: blue = 0
    return red, green, blue

class Square:
    def __init__(self, y_value):
        self.y_value = y_value * (SQUARE_SIZE + SQUARE_SPACER)
        self.color = pmma.ColorConverter()
        self.difference = [random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20)]
        self.path = []
        v = random.randint(0, 1)

        if v == 0:
            self.x_displacement = random.randint(-(display.get_width()-(SQUARE_X_CENTER+SQUARE_SIZE*2)), int(SQUARE_SIZE*1.1))
        else:
            self.x_displacement = random.randint(int(SQUARE_SIZE*1.1), (display.get_width()-(SQUARE_X_CENTER+SQUARE_SIZE*2)))
        self.generate_path(y_value)

    def generate_path(self, index):
        self.path = [[SQUARE_X_CENTER, self.y_value]]
        new_y_value = index * (SQUARE_SIZE + SQUARE_SPACER)
        y_distance = new_y_value - self.y_value
        x_distance = self.x_displacement

        split = int((60 * ANIMATION_DURATION-1)/3)

        x_delta = x_distance / split
        for i in range(split):
            self.path.append([self.path[-1][0] + x_delta, self.path[-1][1]])

        y_delta = y_distance / split
        for i in range(split):
            self.path.append([self.path[-1][0], self.path[-1][1] + y_delta])

        for i in range(split):
            self.path.append([self.path[-1][0] - x_delta, self.path[-1][1]])

        for x in range(((ANIMATION_DURATION * 60) - len(self.path))+1):
            self.path.append([*self.path[-1]])

        self.y_value = new_y_value
        v = random.randint(0, 1)
        if v == 0:
            self.x_displacement = random.randint(-(display.get_width()-(SQUARE_X_CENTER+SQUARE_SIZE*2)), int(SQUARE_SIZE*1.1))
        else:
            self.x_displacement = random.randint(int(SQUARE_SIZE*1.1), (display.get_width()-(SQUARE_X_CENTER+SQUARE_SIZE*2)))

    def render(self, timer, frame_index):
        x, y = self.path[frame_index]
        #print(x, y)
        color = self.color.generate_color_from_perlin_noise(timer/25)
        pygame.draw.rect(display, color, [x, y+SQUARE_Y_OFFSET, SQUARE_SIZE, SQUARE_SIZE])
        pygame.draw.rect(display, apply_color_offset(color, self.difference), [x, y+SQUARE_Y_OFFSET, SQUARE_SIZE, SQUARE_SIZE], width=3)

square_indexes = []
squares_array = []
for i in range(SQUARE_COUNT):
    squares_array.append(Square(i))
    square_indexes.append(i)

start = time.perf_counter()
now_time = 0
frame_index = 0
surface = pygame.Surface(display.get_size())
surface.fill([255, 255, 255])
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if frame_index > ANIMATION_DURATION * 60:
        frame_index = 0
        random.shuffle(square_indexes)
        frame_index = 0
        i = 0
        for square in squares_array:
            square.generate_path(square_indexes[i])
            i += 1

    surface.blit(display, (0, 0))
    display.fill([255, 255, 255])
    surface.set_alpha(220) # 200
    display.blit(surface, (0, 0))

    for square in squares_array:
        square.render(now_time, frame_index)

    pygame.display.flip()

    clock.tick(60)
    frame_index += 1
    now_time = time.perf_counter() - start