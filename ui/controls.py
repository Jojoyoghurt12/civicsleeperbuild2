import pygame


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
        pygame.draw.rect(screen, (230, 230, 230), button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 1)
        button_text = font.render(label, True, (0, 0, 0))
        screen.blit(
            button_text,
            (
                button_rect.centerx - button_text.get_width() // 2,
                button_rect.centery - button_text.get_height() // 2,
            )
        )


def draw_km_step_buttons(screen, km_sliders, step_button_size, step_button_gap, font):
    for substrate, slider in km_sliders:
        button_x = slider.x + slider.width - (2 * step_button_size + step_button_gap)
        button_y = slider.y + 25
        km_step_buttons = [
            (pygame.Rect(button_x, button_y, step_button_size, step_button_size), "-"),
            (pygame.Rect(button_x + step_button_size + step_button_gap, button_y, step_button_size, step_button_size), "+"),
        ]
        for button_rect, label in km_step_buttons:
            pygame.draw.rect(screen, (230, 230, 230), button_rect)
            pygame.draw.rect(screen, (0, 0, 0), button_rect, 1)
            button_text = font.render(label, True, (0, 0, 0))
            screen.blit(
                button_text,
                (
                    button_rect.centerx - button_text.get_width() // 2,
                    button_rect.centery - button_text.get_height() // 2,
                )
            )


def draw_total_atp_button(screen, button_rect, show_total_atp, font):
    fill = (190, 220, 190) if show_total_atp else (230, 230, 230)
    pygame.draw.rect(screen, fill, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 1)
    text = font.render("Total ATP", True, (0, 0, 0))
    screen.blit(
        text,
        (
            button_rect.centerx - text.get_width() // 2,
            button_rect.centery - text.get_height() // 2,
        )
    )


def draw_pathway_tabs(screen, pathway_tab_rects, pathway_reactions, selected_tab, font, extra_section_heights=None):
    pathway_colors = {
        "Starting parameters": ((190, 224, 183), (226, 243, 222)),
        "Glycolysis": ((183, 217, 255), (222, 239, 255)),
        "Citric acid cycle": ((244, 206, 157), (252, 232, 205)),
        "Fructose pathways": ((214, 190, 235), (237, 224, 247)),
    }

    for pathway_name, tab_rect in pathway_tab_rects:
        has_reactions = pathway_name in (extra_section_heights or {}) or len(pathway_reactions[pathway_name]) > 0
        selected_color, idle_color = pathway_colors.get(pathway_name, ((210, 230, 255), (230, 230, 230)))
        if pathway_name == selected_tab:
            tab_color = selected_color
        elif has_reactions:
            tab_color = idle_color
        else:
            tab_color = (225, 225, 225)

        pygame.draw.rect(screen, tab_color, tab_rect)
        pygame.draw.rect(screen, (0, 0, 0), tab_rect, 1)
        tab_text_color = (0, 0, 0) if has_reactions else (120, 120, 120)
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
        fill_color = (210, 230, 255) if reaction_name == selected_reaction else (230, 230, 230)
        pygame.draw.rect(screen, fill_color, button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 1)
        button_text = font.render(reaction_name, True, (0, 0, 0))
        screen.blit(button_text, (button_rect.x + 4, button_rect.y + 3))
