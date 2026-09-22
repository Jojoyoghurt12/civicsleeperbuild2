import pygame


COLORS = {
    "background": (244, 247, 245),
    "surface": (255, 255, 252),
    "surface_alt": (236, 242, 238),
    "border": (196, 207, 200),
    "border_strong": (92, 118, 106),
    "text": (26, 35, 31),
    "muted": (91, 105, 98),
    "disabled_text": (142, 151, 146),
    "disabled_fill": (229, 233, 230),
    "accent": (43, 132, 104),
    "accent_soft": (206, 232, 222),
    "accent_hover": (222, 240, 233),
    "danger": (188, 54, 62),
    "danger_soft": (248, 221, 224),
    "info": (65, 116, 177),
    "info_soft": (218, 233, 249),
    "warning_soft": (250, 229, 199),
    "purple_soft": (235, 224, 246),
}

PATHWAY_COLORS = {
    "Starting parameters": (COLORS["accent_soft"], (232, 244, 238)),
    "Glycolysis": (COLORS["info_soft"], (232, 241, 251)),
    "Citric acid cycle": (COLORS["warning_soft"], (253, 241, 224)),
    "Fructose pathways": (COLORS["purple_soft"], (244, 237, 250)),
    "Exchange reactions": (COLORS["accent_soft"], (232, 244, 238)),
    "Biomass demands": ((229, 229, 247), (240, 240, 250)),
}


def font(size, bold=False):
    return pygame.font.SysFont("segoeui", size, bold=bold) or pygame.font.SysFont(None, size, bold=bold)


def draw_panel(screen, rect, fill=None, border=None):
    pygame.draw.rect(screen, fill or COLORS["surface"], rect, border_radius=8)
    pygame.draw.rect(screen, border or COLORS["border"], rect, 1, border_radius=8)


def draw_text(screen, text, font_obj, color, position, anchor="center"):
    rendered_text = font_obj.render(text, True, color)
    text_rect = rendered_text.get_rect()
    setattr(text_rect, anchor, position)
    screen.blit(rendered_text, text_rect)


def draw_button(screen, rect, label, font_obj, selected=False, enabled=True, align="center"):
    if not enabled:
        fill = COLORS["disabled_fill"]
        border = COLORS["border"]
        text_color = COLORS["disabled_text"]
    elif selected:
        fill = COLORS["accent_soft"]
        border = COLORS["accent"]
        text_color = COLORS["text"]
    else:
        fill = COLORS["surface"]
        border = COLORS["border"]
        text_color = COLORS["text"]

    pygame.draw.rect(screen, fill, rect, border_radius=6)
    pygame.draw.rect(screen, border, rect, 1, border_radius=6)
    text = font_obj.render(label, True, text_color)
    if align == "left":
        text_x = rect.x + 10
    else:
        text_x = rect.centerx - text.get_width() // 2
    text_rect = text.get_rect()
    text_rect.centery = rect.centery
    text_rect.x = text_x
    screen.blit(text, text_rect)


def draw_menu_button(screen, rect, selected=False):
    fill = COLORS["accent_soft"] if selected else COLORS["surface"]
    border = COLORS["accent"] if selected else COLORS["border"]
    pygame.draw.rect(screen, fill, rect, border_radius=6)
    pygame.draw.rect(screen, border, rect, 1, border_radius=6)
    line_width = max(18, rect.width - 18)
    line_left = rect.centerx - line_width // 2
    for offset in (-6, 0, 6):
        y = rect.centery + offset
        pygame.draw.line(screen, COLORS["text"], (line_left, y), (line_left + line_width, y), 2)


def draw_pill_button(screen, rect, label, font_obj, selected=False, enabled=True):
    draw_button(screen, rect, label, font_obj, selected=selected, enabled=enabled)


def draw_danger_button(screen, rect, label, font_obj):
    pygame.draw.rect(screen, COLORS["danger_soft"], rect, border_radius=6)
    pygame.draw.rect(screen, COLORS["danger"], rect, 1, border_radius=6)
    draw_text(screen, label, font_obj, COLORS["danger"], rect.center)