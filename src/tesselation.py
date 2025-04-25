import pmma

pmma.init()

display = pmma.Display()
display.create()

events = pmma.Events()
general = pmma.General()

class Tile:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

        self.polygon = pmma.RadialPolygon()
        self.polygon.set_point_count(8)
        self.polygon.set_radius(radius)
        self.polygon.set_center((x, y))
        self.polygon.set_width(3)

        self.noise = pmma.Perlin(seed=0)

    def render(self):
        x = general.get_application_run_time() + self.x / (display.get_width() / 2)
        y = general.get_application_run_time() + self.y / (display.get_height() / 2)

        new_radius = self.noise.generate_2D_perlin_noise(x, y, new_range=[self.radius * 0.8, self.radius * 1.2])
        self.polygon.set_radius(new_radius)

        self.polygon.generate_color_from_perlin_noise()

        self.polygon.set_rotation(general.get_application_run_time())
        self.polygon.render()

# Dynamically calculate tile layout
tile_count_x = 13  # You can tweak this to control number of tiles
tile_count_y = 8   # Or make it adaptive

screen_width = display.get_width()
screen_height = display.get_height()

tile_spacing_x = screen_width / tile_count_x
tile_spacing_y = screen_height / tile_count_y

tile_radius = min(tile_spacing_x, tile_spacing_y) / 2

tiles = []
for i in range(tile_count_x):
    for j in range(tile_count_y):
        center_x = (i + 0.5) * tile_spacing_x
        center_y = (j + 0.5) * tile_spacing_y
        tiles.append(Tile(center_x, center_y, tile_radius))

while True:
    events.handle()
    display.clear()

    for tile in tiles:
        tile.render()

    general.compute()
    display.refresh()
