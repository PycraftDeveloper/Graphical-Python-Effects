# type: ignore

import pmma, random, math, time

def calculate_number_of_pixels(radius):
    count = 0
    for i in range(radius, radius - 3, -1):
        count += 1 + ((2 * math.pi) / math.asin(1 / i)) * 0.27341772151898736

    return int(count)

def lerp(start, end, duration, elapsed):
    if elapsed >= duration:
        return end

    if elapsed <= 0:
        return start

    return [(end[0] - start[0]) * (elapsed / duration) + start[0], (end[1] - start[1]) * (elapsed / duration) + start[1]]

CENTER = [1920 // 2, 1080 // 2]

class Point(pmma.Shapes2D.Pixel):
    def __init__(self, angle):
        super().__init__()

        self.shape_center.set_coords([0, 0])
        self.shape_color.generate_from_random()
        self.angle = angle
        self.start = time.perf_counter()
        self.start_point = CENTER
        self.end_point = CENTER
        self.duration = 1 + random.random() * 2
        self.shape_color.configure(seed=0)
        self.angle_value = math.sin(angle)
        self.start_delay = 0
        self.end_delay = 0

    def set_end(self, radius):
        point = [CENTER[0] + math.cos(self.angle) * radius, CENTER[1] + math.sin(self.angle) * radius]
        self.start_point = self.end_point
        self.end_point = point
        self.duration = 1.5 + random.random() * 1.5
        self.start = time.perf_counter()
        split = random.random()
        self.start_delay = (3 - self.duration) * split
        self.end_delay = (3 - self.duration) * (1 - split)

    def render(self):
        self.shape_color.generate_from_perlin_noise(self.angle_value + time.perf_counter())
        self.shape_center.set_coords(lerp(self.start_point, self.end_point, self.duration - self.end_delay, (time.perf_counter() - self.start_delay) - self.start))
        super().render()

display = pmma.Display()
display.create([1920, 1080], fullscreen=False, vsync=False)

time.sleep(2)

current_radius = 0
next_radius = CENTER[1]
#next_number_of_points = calculate_number_of_pixels(next_radius)

points = []
for r in range(0, 36, 1):
    for i in range(1080):
        angle = ((2 * math.pi) / 1080) * i
        points.append(Point(angle))
        points[-1].set_end(next_radius - r)

start = time.perf_counter() # move for 3, appreciate for one
app_start = time.perf_counter()
#display.window_fill_color.set_RGB([0, 0, 0])

while True:
    if time.perf_counter() - start >= 4:
        start = time.perf_counter()
        current_radius = next_radius
        if time.perf_counter() - app_start < 9:
            next_radius = 0
        else:
            next_radius = random.randint(100, CENTER[1])
            while abs(next_radius - current_radius) < 100:
                next_radius = random.randint(100, CENTER[1])
        #next_number_of_points = calculate_number_of_pixels(next_radius)

        # issue here
        r = 0
        count = 0
        for point in points:
            point.set_end(next_radius - r)
            count += 1
            if count % 1080 == 0:
                r += 1


    display.clear()

    for point in points:
        point.render()

    display.continuous_refresh(refresh_rate=0)

# 8 FPS