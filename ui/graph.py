import math
import pygame

from ui import theme

TOTAL_ATP_LABEL = "Total ATP"


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


def make_curves(results, curve_colors, show_total_atp):
    curves = []
    for i, (metabolite, values) in enumerate(results.items()):
        if metabolite == TOTAL_ATP_LABEL and not show_total_atp:
            continue

        color = (0, 0, 0) if metabolite == TOTAL_ATP_LABEL else curve_colors[i % len(curve_colors)]
        curves.append((metabolite, values, color))
    return curves


def get_max_value(results, show_total_atp, hidden_metabolites=None):
    hidden_metabolites = hidden_metabolites or set()
    all_values = []
    for metabolite, values in results.items():
        if metabolite == TOTAL_ATP_LABEL and not show_total_atp:
            continue
        if metabolite in hidden_metabolites:
            continue
        all_values += values
    if not all_values:
        return 1
    return max(1, math.ceil(max(all_values)))


def draw_axes(screen, results, graph_left, graph_top, graph_width, graph_height, max_value):
    graph_bottom = graph_top + graph_height
    graph_rect = pygame.Rect(graph_left - 12, graph_top - 12, graph_width + 24, graph_height + 24)
    theme.draw_panel(screen, graph_rect)
    pygame.draw.line(screen, theme.COLORS["border_strong"], (graph_left, graph_bottom), (graph_left + graph_width, graph_bottom), 2)
    pygame.draw.line(screen, theme.COLORS["border_strong"], (graph_left, graph_top), (graph_left, graph_bottom), 2)

    axis_font = theme.font(17)
    axis_title_font = theme.font(22)

    x_title = axis_title_font.render("Time", True, theme.COLORS["text"])
    screen.blit(x_title, (graph_left + graph_width // 2 - x_title.get_width() // 2, graph_bottom + 35))

    y_title = axis_title_font.render("Amount", True, theme.COLORS["text"])
    screen.blit(y_title, (graph_left, graph_top - 30))

    x_tick_count = 5
    time_steps = len(next(iter(results.values())))
    for i in range(x_tick_count + 1):
        fraction = i / x_tick_count
        x = graph_left + fraction * graph_width
        y = graph_bottom
        time_value = int(fraction * (time_steps - 1))
        pygame.draw.line(screen, theme.COLORS["surface_alt"], (x, graph_top), (x, graph_bottom), 1)
        pygame.draw.line(screen, theme.COLORS["border_strong"], (x, y), (x, y + 6), 2)
        text = axis_font.render(str(time_value), True, theme.COLORS["muted"])
        screen.blit(text, (x - 10, y + 10))

    y_tick_count = 5
    for i in range(y_tick_count + 1):
        fraction = i / y_tick_count
        x = graph_left
        y = graph_bottom - fraction * graph_height
        value = fraction * max_value
        pygame.draw.line(screen, theme.COLORS["surface_alt"], (graph_left, y), (graph_left + graph_width, y), 1)
        pygame.draw.line(screen, theme.COLORS["border_strong"], (x - 6, y), (x, y), 2)
        text = axis_font.render(f"{value:.0f}", True, theme.COLORS["muted"])
        screen.blit(text, (x - 45, y - 8))


def draw_curves(screen, curves, graph_left, graph_top, graph_width, graph_height, max_value, highlighted_metabolite, downsample_step, hidden_metabolites=None):
    hidden_metabolites = hidden_metabolites or set()
    visible_curves = [curve for curve in curves if curve[0] not in hidden_metabolites]
    ordered_curves = [curve for curve in visible_curves if curve[0] != highlighted_metabolite]
    ordered_curves += [curve for curve in visible_curves if curve[0] == highlighted_metabolite]
    for label, values, color in ordered_curves:
        draw_values = downsample_values(values, downsample_step)
        points = values_to_points(draw_values, graph_left, graph_top, graph_width, graph_height, max_value)

        if label == highlighted_metabolite:
            line_width = 7
        elif label == TOTAL_ATP_LABEL:
            line_width = 5
        else:
            line_width = 2
        for i in range(len(points) - 1):
            pygame.draw.line(screen, color, points[i], points[i + 1], line_width)


def draw_legend(screen, curves, graph_left, graph_top, graph_width, highlighted_metabolite, pathway_metabolites, selected_legend_pathway, hidden_metabolites=None):
    hidden_metabolites = hidden_metabolites or set()
    legend_font = theme.font(20)
    toggle_font = theme.font(15)
    legend_x = graph_left + graph_width + 30
    legend_y = graph_top + 20
    legend_button_rects = []
    legend_pathway_tab_rects = []
    legend_toggle_button_rects = []
    legend_pathway_toggle_button_rects = []
    primary_curves = []
    cofactor_curves = []
    metabolite_curves = []

    for curve in curves:
        label = curve[0]
        label_lower = label.lower()
        if label_lower in ("glucose", "fructose", "gtp") or "atp" in label_lower:
            primary_curves.append(curve)
        elif label_lower in ("nadh", "pi", "adp", "nad+", "fad", "fadh2", "co2"):
            cofactor_curves.append(curve)
        else:
            metabolite_curves.append(curve)

    def draw_legend_item(label, color, item_x, item_y, show_toggle):
        accordion_right = legend_x - 6 + 290
        toggle_width = 58
        if show_toggle:
            toggle_rect = pygame.Rect(accordion_right - toggle_width, item_y - 14, toggle_width, 22)
            legend_rect = pygame.Rect(item_x - 8, item_y - 15, toggle_rect.x - item_x - 4, 30)
            legend_toggle_button_rects.append((label, toggle_rect))
        else:
            toggle_rect = None
            label_width = legend_font.size(label)[0]
            legend_rect = pygame.Rect(item_x - 8, item_y - 15, 35 + label_width + 12, 30)
        legend_button_rects.append((label, legend_rect))
        if label == highlighted_metabolite:
            pygame.draw.rect(screen, theme.COLORS["info_soft"], legend_rect, border_radius=4)
            pygame.draw.rect(screen, theme.COLORS["info"], legend_rect, 1, border_radius=4)

        legend_line_width = 7 if label == highlighted_metabolite else 4
        item_color = (150, 150, 150) if label in hidden_metabolites else color
        text_color = theme.COLORS["disabled_text"] if label in hidden_metabolites else theme.COLORS["text"]
        pygame.draw.line(screen, item_color, (item_x, item_y), (item_x + 25, item_y), legend_line_width)
        label_text = legend_font.render(label, True, text_color)
        screen.blit(label_text, (item_x + 35, item_y - 10))

        if show_toggle:
            theme.draw_button(screen, toggle_rect, "toggle", toggle_font, selected=label not in hidden_metabolites)

    def draw_pathway_tab(pathway_name, tab_rect, has_metabolites, pathway_curves):
        if pathway_name == selected_legend_pathway:
            fill_color = theme.COLORS["info_soft"]
        elif has_metabolites:
            fill_color = theme.COLORS["surface"]
        else:
            fill_color = theme.COLORS["disabled_fill"]

        pygame.draw.rect(screen, fill_color, tab_rect, border_radius=6)
        pygame.draw.rect(screen, theme.COLORS["border"], tab_rect, 1, border_radius=6)
        text_color = theme.COLORS["text"] if has_metabolites else theme.COLORS["disabled_text"]
        tab_text = legend_font.render(pathway_name, True, text_color)
        screen.blit(tab_text, (tab_rect.x + 6, tab_rect.centery - tab_text.get_height() // 2))

        if pathway_name == selected_legend_pathway and pathway_curves:
            toggle_rect = pygame.Rect(tab_rect.right - 74, tab_rect.y + 2, 68, tab_rect.height - 4)
            pathway_labels = [label for label, values, color in pathway_curves]
            all_hidden = all(label in hidden_metabolites for label in pathway_labels)
            theme.draw_button(screen, toggle_rect, "all on" if all_hidden else "all off", toggle_font, selected=all_hidden)
            legend_pathway_toggle_button_rects.append((pathway_name, pathway_labels, toggle_rect))

    for i, (label, values, color) in enumerate(primary_curves):
        draw_legend_item(label, color, legend_x, legend_y + i * 25, False)

    for i, (label, values, color) in enumerate(cofactor_curves):
        draw_legend_item(label, color, legend_x + 165, legend_y + i * 25, False)

    top_group_height = max(len(primary_curves), len(cofactor_curves)) * 25
    divider_color = theme.COLORS["border"]
    metabolite_top = legend_y + top_group_height + 18
    if metabolite_curves and (primary_curves or cofactor_curves):
        divider_y = metabolite_top - 20
        pygame.draw.line(screen, divider_color, (legend_x - 6, divider_y), (legend_x + 274, divider_y), 4)

    tab_y = metabolite_top
    tab_width = 290
    tab_height = 22
    tab_gap = 6
    item_gap = 25
    for pathway_name, pathway_metabolite_names in pathway_metabolites.items():
        pathway_curves = [
            curve
            for curve in metabolite_curves
            if curve[0] in pathway_metabolite_names
        ]
        tab_rect = pygame.Rect(legend_x - 6, tab_y - 14, tab_width, tab_height)
        legend_pathway_tab_rects.append((pathway_name, tab_rect))
        draw_pathway_tab(pathway_name, tab_rect, len(pathway_curves) > 0, pathway_curves)
        tab_y += tab_height + tab_gap

        if pathway_name == selected_legend_pathway:
            for i, (label, values, color) in enumerate(pathway_curves):
                draw_legend_item(label, color, legend_x, tab_y + i * item_gap, True)
            tab_y += len(pathway_curves) * item_gap

    return legend_button_rects, legend_pathway_tab_rects, legend_toggle_button_rects, legend_pathway_toggle_button_rects
