import pygame

from ui import theme


def make_step_button_rects(sliders):
    step_button_size = 24
    step_button_gap = 8
    step_buttons = []
    for slider, step in sliders:
        button_x = slider.x + slider.width - (2 * step_button_size + step_button_gap)
        button_y = slider.y + 25
        minus_button = pygame.Rect(button_x, button_y, step_button_size, step_button_size)
        plus_button = pygame.Rect(button_x + step_button_size + step_button_gap, button_y, step_button_size, step_button_size)
        step_buttons.append((minus_button, slider, -step, "-"))
        step_buttons.append((plus_button, slider, step, "+"))
    return step_buttons


def make_sidebar_tab_names(pathway_reactions, extra_section_heights):
    extra_section_heights = extra_section_heights or {}
    tab_names = list(extra_section_heights)
    tab_names += [pathway_name for pathway_name in pathway_reactions if pathway_name not in tab_names]
    return tab_names


def make_pathway_tab_rects(pathway_reactions, selected_tab, button_left, tab_top, tab_width, tab_height, button_height, button_gap, extra_section_heights=None):
    tab_rects = []
    tab_y = tab_top
    for pathway_name in make_sidebar_tab_names(pathway_reactions, extra_section_heights):
        tab_rects.append((pathway_name, pygame.Rect(button_left, tab_y, tab_width, tab_height)))
        tab_y += tab_height + button_gap
        if pathway_name == selected_tab:
            if pathway_name in (extra_section_heights or {}):
                expanded_height = extra_section_heights[pathway_name]
            else:
                expanded_height = len(pathway_reactions[pathway_name]) * (button_height + button_gap)
            tab_y += expanded_height
    return tab_rects


def make_reaction_button_rects(pathway_reactions, pathway_name, button_left, tab_top, tab_height, button_width, button_height, button_gap, extra_section_heights=None):
    button_rects = []
    button_top = tab_top
    for current_pathway in make_sidebar_tab_names(pathway_reactions, extra_section_heights):
        button_top += tab_height + button_gap
        if current_pathway == pathway_name:
            break

    for i, reaction_name in enumerate(pathway_reactions[pathway_name]):
        button_x = button_left
        button_y = button_top + i * (button_height + button_gap)
        button_rects.append((reaction_name, pygame.Rect(button_x, button_y, button_width, button_height)))
    return button_rects


def draw_step_buttons(screen, step_buttons, font):
    for button_rect, slider, step, label in step_buttons:
        theme.draw_button(screen, button_rect, label, font)


def draw_km_step_buttons(screen, km_sliders, step_button_size, step_button_gap, font):
    for substrate, slider in km_sliders:
        button_x = slider.x + slider.width - (2 * step_button_size + step_button_gap)
        button_y = slider.y + 25
        km_step_buttons = [
            (pygame.Rect(button_x, button_y, step_button_size, step_button_size), "-"),
            (pygame.Rect(button_x + step_button_size + step_button_gap, button_y, step_button_size, step_button_size), "+"),
        ]
        for button_rect, label in km_step_buttons:
            theme.draw_button(screen, button_rect, label, font)


def draw_total_atp_button(screen, button_rect, show_total_atp, font):
    theme.draw_button(screen, button_rect, "Total ATP", font, selected=show_total_atp)


def draw_pathway_tabs(screen, pathway_tab_rects, pathway_reactions, selected_tab, font, extra_section_heights=None):
    for pathway_name, tab_rect in pathway_tab_rects:
        has_reactions = pathway_name in (extra_section_heights or {}) or len(pathway_reactions[pathway_name]) > 0
        selected_color, idle_color = theme.PATHWAY_COLORS.get(pathway_name, (theme.COLORS["accent_soft"], theme.COLORS["surface"]))
        if pathway_name == selected_tab:
            tab_color = selected_color
        elif has_reactions:
            tab_color = idle_color
        else:
            tab_color = theme.COLORS["disabled_fill"]

        pygame.draw.rect(screen, tab_color, tab_rect, border_radius=6)
        border_color = theme.COLORS["accent"] if pathway_name == selected_tab else theme.COLORS["border"]
        pygame.draw.rect(screen, border_color, tab_rect, 1, border_radius=6)
        tab_text_color = theme.COLORS["text"] if has_reactions else theme.COLORS["disabled_text"]
        tab_text = font.render(pathway_name, True, tab_text_color)
        screen.blit(
            tab_text,
            (
                tab_rect.centerx - tab_text.get_width() // 2,
                tab_rect.centery - tab_text.get_height() // 2,
            )
        )


def draw_reaction_buttons(screen, reaction_button_rects, selected_reaction, font):
    for reaction_name, button_rect in reaction_button_rects:
        theme.draw_button(screen, button_rect, reaction_name, font, selected=reaction_name == selected_reaction, align="left")
