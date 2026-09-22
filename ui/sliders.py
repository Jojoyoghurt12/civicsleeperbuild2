import pygame

from ui import theme


class Slider:
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
        self.knob_colour = (0, 0, 0)

    def set_knob_position_fraction(self, fraction):
        fraction = max(0, min(1, fraction))
        self.value = self.min_value + fraction * (self.max_value - self.min_value)

    def get_knob_position_fraction(self):
        return (self.value - self.min_value) / (self.max_value - self.min_value)

    def set_value(self, value):
        value = max(self.min_value, min(self.max_value, value))
        self.value = value

    def draw(self, screen):
        font = theme.font(20)
        title_text = font.render(self.title, True, theme.COLORS["text"])
        screen.blit(title_text, (self.x, self.y - 36))
        pygame.draw.line(screen, theme.COLORS["border"], (self.x, self.y), (self.x + self.width, self.y), 6)
        pygame.draw.line(screen, theme.COLORS["accent"], (self.x, self.y), (self.x + self.get_knob_position_fraction() * self.width, self.y), 6)
        knob_x = self.x + self.get_knob_position_fraction() * self.width
        visual_knob_radius = max(5, self.knob_radius - 2)
        pygame.draw.circle(screen, theme.COLORS["surface"], (int(knob_x), self.y), visual_knob_radius + 3)
        pygame.draw.circle(screen, theme.COLORS["accent"], (int(knob_x), self.y), visual_knob_radius)
        value_text = font.render(f"{self.value:.2f}", True, theme.COLORS["muted"])
        screen.blit(value_text, (self.x + self.width + 10, self.y - 12))

    def handle_event(self, event):
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            knob_x = self.x + self.get_knob_position_fraction() * self.width
            if (mouse_x - knob_x) ** 2 + (mouse_y - self.y) ** 2 <= self.knob_radius ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                changed = True
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                fraction = (mouse_x - self.x) / self.width
                self.set_knob_position_fraction(fraction)

        return changed


def make_km_sliders(reaction_params, reaction_name, control_left):
    km_values = reaction_params[reaction_name]["km"]
    if not isinstance(km_values, dict):
        km_values = {"reaction": km_values}

    sliders = []
    for index, (substrate, value) in enumerate(km_values.items()):
        slider_y = 650 + index * 55
        sliders.append(
            (substrate, Slider(0, 5, value, control_left, slider_y, 200, 10, f"km {substrate}"))
        )

    return sliders
