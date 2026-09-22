import pygame

from computation import engine
from computation.pathways import build_pathway_reactions
from ui.controls import (
    draw_km_step_buttons,
    draw_pathway_tabs,
    draw_reaction_buttons,
    draw_step_buttons,
    draw_total_atp_button,
    make_pathway_tab_rects,
    make_reaction_button_rects,
    make_step_button_rects,
)
from ui.graph import draw_axes, draw_curves, draw_legend, get_max_value, make_curves
from ui.sliders import Slider, make_km_sliders


pygame.init()

WIDTH = 1500
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flux Dynamics Demo")

clock = pygame.time.Clock()

control_left = 390

button_left = 20
tab_top = 20
tab_width = 300
tab_height = 24
button_width = 300
button_height = 20
button_gap = 6

graph_left = control_left
graph_top = 50
graph_width = 700
graph_height = 450

step_button_size = 24
step_button_gap = 8
draw_downsample_step = 4

reaction_params = engine.copy_reaction_params()
reaction_names = list(reaction_params)
pathway_reactions = build_pathway_reactions(reaction_names)
parameter_tab_name = "Starting parameters"
parameter_control_left = button_left + 12
parameter_slider_top = tab_top + tab_height + button_gap + 28
parameter_slider_width = 210
parameter_slider_gap = 64
sidebar_extra_section_heights = {parameter_tab_name: 390}
selected_pathway = "Glycolysis"
selected_sidebar_tab = None
selected_reaction = pathway_reactions[selected_pathway][0]

km_sliders = make_km_sliders(reaction_params, selected_reaction, control_left)
selected_max_flow = Slider(0, 5, reaction_params[selected_reaction]["max_flow"], control_left + 300, 650, 200, 10, "max_flow")
start_slid = Slider(0, 5, 2, parameter_control_left, parameter_slider_top, parameter_slider_width, 10, "glucose start")
fructose_slid = Slider(0, 5, 0, parameter_control_left, parameter_slider_top + parameter_slider_gap, parameter_slider_width, 10, "fructose start")
atp_slid = Slider(0, 10, 5, parameter_control_left, parameter_slider_top + 2 * parameter_slider_gap, parameter_slider_width, 10, "initial ATP")
oxygen_slid = Slider(0, 1, 1, parameter_control_left, parameter_slider_top + 3 * parameter_slider_gap, parameter_slider_width, 10, "oxygen")
time_slid = Slider(100, 4000, 400, parameter_control_left, parameter_slider_top + 4 * parameter_slider_gap, parameter_slider_width, 10, "time steps")
starting_parameter_sliders = [start_slid, fructose_slid, atp_slid, oxygen_slid, time_slid]

show_total_atp = True
highlighted_metabolite = None
hidden_metabolites = set()
legend_button_rects = []
legend_pathway_tab_rects = []
legend_toggle_button_rects = []
selected_legend_pathway = None
total_atp_button = pygame.Rect(parameter_control_left, parameter_slider_top + 320, 210, 28)

max_flow_step_buttons = make_step_button_rects([
    (selected_max_flow, 1.0),
])
starting_parameter_step_buttons = make_step_button_rects([
    (start_slid, 0.2),
    (fructose_slid, 0.2),
    (atp_slid, 0.5),
    (oxygen_slid, 0.1),
    (time_slid, 100),
])

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


def run_simulation():
    return engine.comp_loop(
        reaction_params=reaction_params,
        start_slid=start_slid.value,
        atp_start=atp_slid.value,
        fructose_start=fructose_slid.value,
        oxygen_level=oxygen_slid.value,
        simulation_steps=time_slid.value,
    )


def update_selected_reaction(reaction_name):
    global selected_reaction, km_sliders
    selected_reaction = reaction_name
    km_sliders = make_km_sliders(reaction_params, selected_reaction, control_left)
    selected_max_flow.set_value(reaction_params[selected_reaction]["max_flow"])


def update_simulation():
    global results, max_value, curves
    for substrate, slider in km_sliders:
        engine.set_reaction_substrate_km_value(reaction_params, selected_reaction, substrate, slider.value)
    reaction_params[selected_reaction]["max_flow"] = selected_max_flow.value
    results = run_simulation()
    max_value = get_max_value(results, show_total_atp, hidden_metabolites)
    curves = make_curves(results, curve_colors, show_total_atp)


def make_pathway_metabolites(pathway_reactions, reaction_params):
    reactions_by_name = {
        reaction["name"]: reaction
        for reaction in engine.build_reactions(engine.copy_reaction_params(reaction_params))
    }
    pathway_metabolites = {}
    for pathway_name, reaction_list in pathway_reactions.items():
        metabolites = set()
        for reaction_name in reaction_list:
            reaction = reactions_by_name[reaction_name]
            metabolites.update(reaction["reactants"])
            metabolites.update(reaction["products"])
        pathway_metabolites[pathway_name] = metabolites
    return pathway_metabolites


def make_sidebar_rects():
    tab_rects = make_pathway_tab_rects(
        pathway_reactions,
        selected_sidebar_tab,
        button_left,
        tab_top,
        tab_width,
        tab_height,
        button_height,
        button_gap,
        sidebar_extra_section_heights,
    )
    if selected_sidebar_tab in pathway_reactions:
        button_rects = make_reaction_button_rects(
            pathway_reactions,
            selected_sidebar_tab,
            button_left,
            tab_top,
            tab_height,
            button_width,
            button_height,
            button_gap,
            sidebar_extra_section_heights,
        )
    else:
        button_rects = []
    return tab_rects, button_rects


results = run_simulation()
max_value = get_max_value(results, show_total_atp, hidden_metabolites)
curves = make_curves(results, curve_colors, show_total_atp)

button_font = pygame.font.SysFont(None, 18)
pathway_tab_rects, reaction_button_rects = make_sidebar_rects()
pathway_metabolites = make_pathway_metabolites(pathway_reactions, reaction_params)

running = True
while running:
    slider_changed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected_sidebar_tab == parameter_tab_name and total_atp_button.collidepoint(event.pos):
                show_total_atp = not show_total_atp
                max_value = get_max_value(results, show_total_atp, hidden_metabolites)
                curves = make_curves(results, curve_colors, show_total_atp)

            for legend_label, toggle_rect in legend_toggle_button_rects:
                if toggle_rect.collidepoint(event.pos):
                    if legend_label in hidden_metabolites:
                        hidden_metabolites.remove(legend_label)
                    else:
                        hidden_metabolites.add(legend_label)
                    max_value = get_max_value(results, show_total_atp, hidden_metabolites)

            for legend_label, legend_rect in legend_button_rects:
                if legend_rect.collidepoint(event.pos):
                    highlighted_metabolite = None if highlighted_metabolite == legend_label else legend_label

            for pathway_name, tab_rect in legend_pathway_tab_rects:
                if tab_rect.collidepoint(event.pos):
                    selected_legend_pathway = None if selected_legend_pathway == pathway_name else pathway_name

            for pathway_name, tab_rect in pathway_tab_rects:
                if tab_rect.collidepoint(event.pos):
                    if pathway_name == selected_sidebar_tab:
                        selected_sidebar_tab = None
                        pathway_tab_rects, reaction_button_rects = make_sidebar_rects()
                    elif pathway_name == parameter_tab_name:
                        selected_sidebar_tab = parameter_tab_name
                        pathway_tab_rects, reaction_button_rects = make_sidebar_rects()
                    elif pathway_reactions[pathway_name]:
                        selected_sidebar_tab = pathway_name
                        selected_pathway = pathway_name
                        pathway_tab_rects, reaction_button_rects = make_sidebar_rects()
                        update_selected_reaction(pathway_reactions[selected_pathway][0])
                        slider_changed = True

            for reaction_name, button_rect in reaction_button_rects:
                if button_rect.collidepoint(event.pos):
                    update_selected_reaction(reaction_name)
                    slider_changed = True

            if selected_sidebar_tab == parameter_tab_name:
                visible_step_buttons = max_flow_step_buttons + starting_parameter_step_buttons
            else:
                visible_step_buttons = max_flow_step_buttons
            for button_rect, slider, step, label in visible_step_buttons:
                if button_rect.collidepoint(event.pos):
                    slider.set_value(round(slider.value + step, 10))
                    slider_changed = True

            for substrate, slider in km_sliders:
                km_button_x = slider.x + slider.width - (2 * step_button_size + step_button_gap)
                km_button_y = slider.y + 25
                km_minus_button = pygame.Rect(km_button_x, km_button_y, step_button_size, step_button_size)
                km_plus_button = pygame.Rect(km_button_x + step_button_size + step_button_gap, km_button_y, step_button_size, step_button_size)
                if km_minus_button.collidepoint(event.pos):
                    slider.set_value(round(slider.value - 0.1, 10))
                    slider_changed = True
                if km_plus_button.collidepoint(event.pos):
                    slider.set_value(round(slider.value + 0.1, 10))
                    slider_changed = True

        if selected_max_flow.handle_event(event):
            slider_changed = True
        if selected_sidebar_tab == parameter_tab_name:
            for slider in starting_parameter_sliders:
                if slider.handle_event(event):
                    slider_changed = True
        for substrate, slider in km_sliders:
            if slider.handle_event(event):
                slider_changed = True

    if slider_changed:
        update_simulation()

    screen.fill((245, 245, 245))

    for substrate, slider in km_sliders:
        slider.draw(screen)
    selected_max_flow.draw(screen)
    if selected_sidebar_tab == parameter_tab_name:
        for slider in starting_parameter_sliders:
            slider.draw(screen)

    step_font = pygame.font.SysFont(None, 24)
    draw_km_step_buttons(screen, km_sliders, step_button_size, step_button_gap, step_font)
    draw_step_buttons(screen, max_flow_step_buttons, step_font)
    if selected_sidebar_tab == parameter_tab_name:
        draw_step_buttons(screen, starting_parameter_step_buttons, step_font)
        draw_total_atp_button(screen, total_atp_button, show_total_atp, step_font)

    selected_font = pygame.font.SysFont(None, 24)
    selected_text = selected_font.render(f"selected pathway: {selected_pathway} | selected reaction: {selected_reaction}", True, (0, 0, 0))
    screen.blit(selected_text, (control_left, 610))

    draw_pathway_tabs(screen, pathway_tab_rects, pathway_reactions, selected_sidebar_tab, button_font, sidebar_extra_section_heights)
    draw_reaction_buttons(screen, reaction_button_rects, selected_reaction, button_font)

    draw_axes(screen, results, graph_left, graph_top, graph_width, graph_height, max_value)
    draw_curves(screen, curves, graph_left, graph_top, graph_width, graph_height, max_value, highlighted_metabolite, draw_downsample_step, hidden_metabolites)
    legend_button_rects, legend_pathway_tab_rects, legend_toggle_button_rects = draw_legend(
        screen,
        curves,
        graph_left,
        graph_top,
        graph_width,
        highlighted_metabolite,
        pathway_metabolites,
        selected_legend_pathway,
        hidden_metabolites,
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
