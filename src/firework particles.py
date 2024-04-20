try:
    import random
    import time
    import pmma
    import math
    import pygame
    from traceback import format_exception

    WITH_G = True
    COLLISION_WITH_WALL = True

    canvas = pmma.Canvas()
    canvas.create_canvas(1280, 720)
    events = pmma.Events()

    audio_data = pmma.GetAudioData()
    audio_data.start_sampling(input_device_id=9)

    registry = pmma.Registry

    class Particle:
        def __init__(self, vel_x, vel_y):
            self.x = canvas.get_width()/2
            self.y = canvas.get_height()/2
            self.vel_x = vel_x
            self.vel_y = vel_y

            self.fall_time = time.perf_counter()

            self.col = [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]

        def render(self):
            pos = self.x, self.y
            pygame.draw.circle(
                Surface,
                self.col,
                pos, 2)

            if WITH_G:
                self.y += 9.81 * (time.perf_counter() - self.fall_time)

            if COLLISION_WITH_WALL:
                if self.x < 0 or self.x > canvas.get_width():
                    self.vel_x *= -1
                if self.y < 0:
                    self.vel_y *= -1
                    self.fall_time = time.perf_counter()

            self.x += self.vel_x
            self.y += self.vel_y

    particles = []
    particles.append(Particle(1, -20))

    start = time.perf_counter()
    now_time = 0
    v_max = 0.00001
    while registry.running:
        window_size = canvas.get_width(), canvas.get_height()

        Surface = pygame.Surface(window_size).convert()
        Surface.fill((0, 0, 0))

        Surface.set_colorkey((0, 0, 0))
        Surface2 = pygame.Surface(window_size)

        Surface2.fill((0, 0, 0))

        volume = audio_data.get_volume()

        number_of_particles = 1+int((10/v_max)*volume)
        if number_of_particles > 500:
            number_of_particles = 500
        velocity_multiplier = (10/v_max)*volume
        for i in range(int(number_of_particles)):
            particles.append(
                Particle(
                    ((random.random()*2)-1)*velocity_multiplier,
                    -random.random()*velocity_multiplier*2))

        if volume > v_max:
            v_max = volume

        canvas.clear(0, 0, 0)

        new_events = events.handle(canvas)
        for event in new_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    v_max = 0.00001

        particles_2 = []

        for particle in particles:
            particle.render()
            if COLLISION_WITH_WALL:
                if particle.y < canvas.get_height():
                    particles_2.append(particle)
            else:
                if not (particle.y > canvas.get_height() or particle.x > canvas.get_width() or particle.x < 0 or particle.y < 0):
                    particles_2.append(particle)

        particles = particles_2

        Surface2.set_alpha(1) # 10

        canvas.blit(Surface2, (0, 0))

        canvas.blit(Surface, (0, 0))

        canvas.refresh()
        now_time = time.perf_counter() - start
except Exception as error:
    print("".join(
        format_exception(
            None,
            error,
            error.__traceback__)))