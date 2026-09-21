import pygame
import numpy as np
import matplotlib.pyplot as plt
from computation import tester
import math


pygame.init()

WIDTH = 1400
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flux Dynamics Demo")

clock = pygame.time.Clock()
running = True


# create slider class
class Slider:
    # constructor to initialize the slider with min, max, and initial values
    def __init__(self, min_value, max_value, initial_value, x, y, width, knob_radius, title):
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.title = title

        self.x = x
        self.y = y
        self.width = width
        self.knob_radius = knob_radius
        self.dragging = False
        self.knob_colour = (0, 0, 0)  # Default knob color
    # ability to slide the knob based on a fraction of the total range
    def set_knob_position_fraction(self, fraction):
        fraction = max(0, min(1, fraction))
        self.value = self.min_value + fraction * (self.max_value - self.min_value)
    # ability to get the current knob position as a fraction of the total range
    def get_knob_position_fraction(self):
        return (self.value - self.min_value) / (self.max_value - self.min_value)
    def set_value(self, value):
        value = max(self.min_value, min(self.max_value, value))
        self.value = value
    def draw(self, screen):
        font = pygame.font.SysFont(None, 24)

        title_text = font.render(self.title, True, (0, 0, 0))
        screen.blit(title_text, (self.x, self.y - 28))

        # Draw the slider track
        pygame.draw.line(screen, (0, 0, 0), (self.x, self.y), (self.x + self.width, self.y), 5)

        # Draw the knob
        knob_x = self.x + self.get_knob_position_fraction() * self.width
        pygame.draw.circle(screen, self.knob_colour, (int(knob_x), self.y), self.knob_radius)

        # Draw the slider value
        value_text = font.render(f"{self.value:.2f}", True, (0, 0, 0))
        screen.blit(value_text, (self.x + self.width + 10, self.y - 12))

    # only compute after slider moved again. 
    def handle_event(self, event):
        changed = False
        # Check if the mouse is clicking on the knob
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            knob_x = self.x + self.get_knob_position_fraction() * self.width
            if (mouse_x - knob_x) ** 2 + (mouse_y - self.y) ** 2 <= self.knob_radius ** 2:
                self.dragging = True
        # Check if the mouse button is released to stop dragging
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                changed = True
                self.dragging = False
        # Check if the mouse is moving while dragging the knob
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                fraction = (mouse_x - self.x) / self.width
                self.set_knob_position_fraction(fraction)

        return changed

#values to points for projections
def values_to_points(values, graph_left, graph_top, graph_width, graph_height, max_value):
    if max_value == 0:
        max_value = 1

    points = []

    for i, value in enumerate(values):
        x = graph_left + i / (len(values) - 1) * graph_width
        y = graph_top + graph_height - value / max_value * graph_height
        points.append((x, y))

    return points


def downsample_values(values, step):
    if step <= 1 or len(values) <= 2:
        return values

    downsampled = values[::step]
    if downsampled[-1] != values[-1]:
        downsampled.append(values[-1])

    return downsampled

def make_curves(results, curve_colors):
    curves = []
    for i, (metabolite, values) in enumerate(results.items()):
        curves.append((metabolite, values, curve_colors[i % len(curve_colors)]))
    return curves


def get_max_value(results):
    all_values = []
    for values in results.values():
        all_values += values
    return max(1, math.ceil(max(all_values)))


def run_simulation():
    return tester.comp_loop(
        reaction_params=reaction_params,
        start_slid=start_slid.value,
        atp_start=atp_slid.value,
    )


# sliders in format (min_value, max_value, initial_value, x, y, width, knob_radius, title)
reaction_params = tester.copy_reaction_params()
reaction_names = list(reaction_params)
selected_reaction = reaction_names[0]

control_left = 430

selected_km = Slider(0, 5, reaction_params[selected_reaction]["km"], control_left, 650, 200, 10, "km")
selected_max_flow = Slider(0, 5, reaction_params[selected_reaction]["max_flow"], control_left + 300, 650, 200, 10, "max_flow")
start_slid = Slider(0, 1000, 100, 40, 550, 250, 10, "glucose start")
atp_slid = Slider(0, 1000, 100, 40, 620, 250, 10, "ATP start")

sliders = [selected_km, selected_max_flow, start_slid, atp_slid]

step_button_size = 24
step_button_gap = 8
km_minus_button = pygame.Rect(selected_km.x, selected_km.y + 25, step_button_size, step_button_size)
km_plus_button = pygame.Rect(selected_km.x + step_button_size + step_button_gap, selected_km.y + 25, step_button_size, step_button_size)
max_flow_minus_button = pygame.Rect(selected_max_flow.x, selected_max_flow.y + 25, step_button_size, step_button_size)
max_flow_plus_button = pygame.Rect(selected_max_flow.x + step_button_size + step_button_gap, selected_max_flow.y + 25, step_button_size, step_button_size)
start_minus_button = pygame.Rect(start_slid.x, start_slid.y + 25, step_button_size, step_button_size)
start_plus_button = pygame.Rect(start_slid.x + step_button_size + step_button_gap, start_slid.y + 25, step_button_size, step_button_size)
atp_minus_button = pygame.Rect(atp_slid.x, atp_slid.y + 25, step_button_size, step_button_size)
atp_plus_button = pygame.Rect(atp_slid.x + step_button_size + step_button_gap, atp_slid.y + 25, step_button_size, step_button_size)

step_buttons = [
    (km_minus_button, selected_km, -0.1, "-"),
    (km_plus_button, selected_km, 0.1, "+"),
    (max_flow_minus_button, selected_max_flow, -1.0, "-"),
    (max_flow_plus_button, selected_max_flow, 1.0, "+"),
    (start_minus_button, start_slid, -10.0, "-"),
    (start_plus_button, start_slid, 10.0, "+"),
    (atp_minus_button, atp_slid, -10.0, "-"),
    (atp_plus_button, atp_slid, 10.0, "+"),
]

results = run_simulation()

max_value = get_max_value(results)

curve_colors = [
    (80, 80, 80),
    (200, 50, 50),
    (50, 120, 220),
    (50, 160, 90),
    (180, 100, 220),
    (220, 140, 40),
    (40, 170, 170),
    (150, 90, 40),
    (20, 120, 120),
    (120, 80, 200),
    (200, 80, 140),
    (100, 130, 40),
    (40, 40, 160),
    (160, 40, 40),
    (40, 120, 60),
    (120, 120, 120),
]

curves = make_curves(results, curve_colors)
draw_downsample_step = 4

button_font = pygame.font.SysFont(None, 18)
reaction_button_rects = []
button_left = 20
button_top = 50
button_width = 360
button_height = 20
button_gap = 6
for i, reaction_name in enumerate(reaction_names):
    column = 0
    row = i
    button_x = button_left + column * (button_width + button_gap)
    button_y = button_top + row * (button_height + button_gap)
    reaction_button_rects.append((reaction_name, pygame.Rect(button_x, button_y, button_width, button_height)))


# main loop
running = True
while running:
    slider_changed = False
    # event checking
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for reaction_name, button_rect in reaction_button_rects:
                if button_rect.collidepoint(event.pos):
                    selected_reaction = reaction_name
                    selected_km.set_value(reaction_params[selected_reaction]["km"])
                    selected_max_flow.set_value(reaction_params[selected_reaction]["max_flow"])
                    slider_changed = True

            for button_rect, slider, step, label in step_buttons:
                if button_rect.collidepoint(event.pos):
                    slider.set_value(round(slider.value + step, 10))
                    slider_changed = True

        for slider in sliders:
            if slider.handle_event(event):
                slider_changed = True
    # event handling for slider changes
    if slider_changed:
        reaction_params[selected_reaction]["km"] = selected_km.value
        reaction_params[selected_reaction]["max_flow"] = selected_max_flow.value
        results = run_simulation()
        max_value = get_max_value(results)
        curves = make_curves(results, curve_colors)

    
    screen.fill((245, 245, 245))
    for slider in sliders:
        slider.draw(screen)

    step_font = pygame.font.SysFont(None, 24)
    for button_rect, slider, step, label in step_buttons:
        pygame.draw.rect(screen, (230, 230, 230), button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 1)
        button_text = step_font.render(label, True, (0, 0, 0))
        screen.blit(
            button_text,
            (
                button_rect.centerx - button_text.get_width() // 2,
                button_rect.centery - button_text.get_height() // 2,
            )
        )

    selected_font = pygame.font.SysFont(None, 24)
    selected_text = selected_font.render(f"selected reaction: {selected_reaction}", True, (0, 0, 0))
    screen.blit(selected_text, (control_left, 610))

    for reaction_name, button_rect in reaction_button_rects:
        fill_color = (210, 230, 255) if reaction_name == selected_reaction else (230, 230, 230)
        pygame.draw.rect(screen, fill_color, button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 1)
        button_text = button_font.render(reaction_name, True, (0, 0, 0))
        screen.blit(button_text, (button_rect.x + 4, button_rect.y + 3))
    
    graph_left = control_left
    graph_top = 50
    graph_width = 700
    graph_height = 450
    graph_bottom = graph_top + graph_height

    # graph axis
    pygame.draw.line(screen, (0, 0, 0), (graph_left, graph_bottom), (graph_left + graph_width, graph_bottom), 2)
    pygame.draw.line(screen, (0, 0, 0), (graph_left, graph_top), (graph_left, graph_bottom), 2)

    # sim point curves
    for label, values, color in curves:
        draw_values = downsample_values(values, draw_downsample_step)
        points = values_to_points(
            draw_values,
            graph_left,
            graph_top,
            graph_width,
            graph_height,
            max_value
        )

        for i in range(len(points) - 1):
            pygame.draw.line(screen, color, points[i], points[i + 1], 2)
    # legend
    legend_font = pygame.font.SysFont(None, 24)
    legend_x = graph_left + graph_width + 30
    legend_y = graph_top + 20
    for i, (label, values, color) in enumerate(curves):
        legend_column = i // 8
        legend_row = i % 8
        item_x = legend_x + legend_column * 130
        item_y = legend_y + legend_row * 25
        pygame.draw.line(screen, color, (item_x, item_y), (item_x + 25, item_y), 4)
        label_text = legend_font.render(label, True, (0, 0, 0))
        screen.blit(label_text, (item_x + 35, item_y - 10))

    # axis specifications
    axis_font = pygame.font.SysFont(None, 20)
    axis_title_font = pygame.font.SysFont(None, 26)

    x_title = axis_title_font.render("Time", True, (0, 0, 0))
    screen.blit(x_title, (graph_left + graph_width // 2 - x_title.get_width() // 2, graph_bottom + 35))

    y_title = axis_title_font.render("Amount", True, (0, 0, 0))
    screen.blit(y_title, (graph_left - 75, graph_top - 25))

    # axis ticks x
    x_tick_count = 5
    time_steps = len(next(iter(results.values())))

    for i in range(x_tick_count + 1):
        fraction = i / x_tick_count

        x = graph_left + fraction * graph_width
        y = graph_bottom

        time_value = int(fraction * (time_steps - 1))

        pygame.draw.line(screen, (0, 0, 0), (x, y), (x, y + 6), 2)

        text = axis_font.render(str(time_value), True, (0, 0, 0))
        screen.blit(text, (x - 10, y + 10))

    # axis ticks y
    y_tick_count = 5

    for i in range(y_tick_count + 1):
        fraction = i / y_tick_count

        x = graph_left
        y = graph_bottom - fraction * graph_height

        value = fraction * max_value

        pygame.draw.line(screen, (0, 0, 0), (x - 6, y), (x, y), 2)

        text = axis_font.render(f"{value:.0f}", True, (0, 0, 0))
        screen.blit(text, (x - 45, y - 8))

    

    

    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS
pygame.quit()





