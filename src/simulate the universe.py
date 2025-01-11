import pygame
import random
import math
import pmma

# Initialize Pygame
pygame.init()
pmma.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Particle System")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Wipe:
    def __init__(self):
        self.position = [WIDTH / 2, HEIGHT / 2]
        self.radius = 0
        self.do_wipe = False

    def draw(self):
        if self.do_wipe:
            pygame.draw.circle(screen, BLACK, (int(self.position[0]), int(self.position[1])), int(self.radius))
            pygame.draw.circle(screen, WHITE, (int(self.position[0]), int(self.position[1])), int(self.radius), width=10)
            d = 60 - clock.get_fps()
            if d > 7.5:
                self.radius += d*1.5
            else:
                self.radius += 5

        if self.radius > 2210:
            self.do_wipe = False
            self.radius = 0

# Particle class
class Particle:
    def __init__(self, x, y, size=1, vx=0, vy=0):
        self.x = x
        self.y = y
        self.size = size
        self.vx = vx
        self.vy = vy
        self.mass = size  # Mass is proportional to size
        color = pmma.ColorConverter()
        self.color = color.generate_random_color(format=pmma.Constants.RGB)
        self.explosion_size = random.randint(750, 1000)

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce off the edges of the screen
        if self.x - self.size < 0 or self.x + self.size > WIDTH:
            self.vx = -self.vx
        if self.y - self.size < 0 or self.y + self.size > HEIGHT:
            self.vy = -self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def attract(self, other, G=0.5):
        # Calculate distance and direction
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:  # Limit the interaction range
            force = G * (self.mass * other.mass) / distance**2
            fx = force * (dx / distance)
            fy = force * (dy / distance)

            # Apply force to velocities
            self.vx += fx / self.mass
            self.vy += fy / self.mass
            other.vx -= fx / other.mass
            other.vy -= fy / other.mass

    def combine(self, other):
        # Check for collision (simple circle overlap)
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.size + other.size:
            # Combine particles
            total_mass = self.mass + other.mass
            self.vx = (self.vx * self.mass + other.vx * other.mass) / total_mass
            self.vy = (self.vy * self.mass + other.vy * other.mass) / total_mass
            self.size = int(math.sqrt(self.size**2 + other.size**2))
            red = self.color[0]*self.mass + other.color[0]*other.mass
            green = self.color[1]*self.mass + other.color[1]*other.mass
            blue = self.color[2]*self.mass + other.color[2]*other.mass
            self.mass = total_mass
            self.color = (red/total_mass, green/total_mass, blue/total_mass)
            return True
        return False

# Initialize particles
particles = [
    Particle(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50),
             size=random.randint(1, 5),
             vx=random.uniform(-1, 1), vy=random.uniform(-1, 1))
    for _ in range(250)
]

# Main loop
running = True
clock = pygame.time.Clock()

surface = pygame.Surface((WIDTH, HEIGHT))
surface.set_alpha(250)
wiper = Wipe()
while running:
    surface.blit(screen, (0, 0))
    screen.fill(BLACK)
    screen.blit(surface, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update particles
    for i, p1 in enumerate(particles):
        for p2 in particles[i + 1:]:
            p1.attract(p2)
            if p1.combine(p2):
                particles.remove(p2)
        p1.move()
        p1.draw(screen)

        if p1.mass > p1.explosion_size:
            particles.remove(p1)
            # Explosion logic
            num_new_particles = int(p1.explosion_size / 3)  # Number of smaller particles
            for _ in range(num_new_particles):
                angle = random.uniform(0, 2 * math.pi)  # Random angle for direction
                speed = random.uniform(5, 7)  # Speed of the smaller particles
                new_vx = math.cos(angle) * speed
                new_vy = math.sin(angle) * speed
                particles.append(Particle(p1.x + 20 * math.cos(angle), p1.y + 20 * math.sin(angle), size=random.randint(1, 5), vx=new_vx, vy=new_vy))

        if ((p1.x - WIDTH/2)**2 + (p1.y - HEIGHT/2)**2)**0.5 < wiper.radius and wiper.do_wipe:
            try:
                particles.remove(p1)
            except:
                pass

    while len(particles) < 75 and wiper.do_wipe is False:
        particles.append(
            Particle(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50),
                     size=random.randint(1, 5),
                     vx=random.uniform(-1, 1), vy=random.uniform(-1, 1))
        )

    wiper.draw()

    pygame.display.flip()
    clock.tick(60)
    if clock.get_fps() < 10:
        wiper.do_wipe = True

pygame.quit()
