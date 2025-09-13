import pmma, time

display = pmma.Display()
display.create([1920, 1080], fullscreen=False, vsync=False)

x_noise = pmma.FractalBrownianMotion(octaves=3, lacunarity=0.8)
y_noise = pmma.FractalBrownianMotion(octaves=3, lacunarity=0.8)

shapes = []
while pmma.General.is_application_running():
    display.clear()

    shape = pmma.Shapes2D.Circle()
    shape.set_radius(100)
    shape.shape_color.configure(seed=0)
    shape.shape_center.configure(seed=0)
    x = (1 + x_noise.noise_1d(time.perf_counter() / 2)) * display.get_width() / 2
    y = (1 + y_noise.noise_1d(time.perf_counter() / 2)) * display.get_height() / 2
    shape.shape_center.set_coord(x, y)
    shape.shape_color.generate_from_1D_perlin_noise(time.perf_counter(), generate_alpha=False)
    shape.set_width(5)
    shapes.append(shape)

    for shape in shapes:
        shape.render()

    if len(shapes) > 7_500:
        shapes.pop(0)

    display.continuous_refresh(refresh_rate=0)