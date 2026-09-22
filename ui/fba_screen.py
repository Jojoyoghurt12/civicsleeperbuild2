import pygame

try:
    from ..computation import engine, fba_engine
except ImportError:
    from computation import engine, fba_engine

from ui.controls import (
    draw_pathway_tabs,
    draw_reaction_buttons,
    make_pathway_tab_rects,
    make_reaction_button_rects,
)
from ui import theme


class FbaScreen:
    def __init__(
        self,
        screen,
        pathway_reactions,
        reaction_params,
        starting_sliders,
        home_button,
        control_left,
        button_left,
        tab_top,
        tab_width,
        tab_height,
        button_width,
        button_height,
        button_gap,
    ):
        self.screen = screen
        self.reaction_params = reaction_params
        self.pathway_reactions = {
            pathway_name: list(reaction_names)
            for pathway_name, reaction_names in pathway_reactions.items()
        }
        self.pathway_reactions["Exchange reactions"] = list(fba_engine.EXCHANGE_REACTION_NAMES)
        self.pathway_reactions["Biomass demands"] = list(fba_engine.BIOMASS_DEMAND_REACTION_NAMES)
        self.starting_sliders = starting_sliders
        self.home_button = home_button
        self.control_left = control_left
        self.button_left = button_left
        self.tab_top = tab_top
        self.tab_width = tab_width
        self.tab_height = tab_height
        self.button_width = button_width
        self.button_height = button_height
        self.button_gap = button_gap
        self.reactions_by_name = {
            reaction["name"]: reaction
            for reaction in fba_engine.build_fba_reactions(engine.copy_reaction_params(self.reaction_params))
        }

        self.selected_pathway = "Exchange reactions"
        self.selected_sidebar_tab = None
        self.selected_reaction = "ATP_demand"
        self.selected_flux_tab = "Exchange reactions"
        self.objective_reaction = self.selected_reaction
        self.reaction_bounds = {}
        self.bound_step = 0.5
        self.use_max_flow_bounds = True
        self.use_steady_state_balance = True
        self.force_full_respiration = True
        self.max_flow_button = pygame.Rect(self.control_left, 130, 230, 32)
        self.steady_state_button = pygame.Rect(self.control_left, 174, 230, 32)
        self.full_respiration_button = pygame.Rect(self.control_left, 218, 230, 32)
        self.lower_minus_button = pygame.Rect(self.control_left + 190, 348, 28, 24)
        self.lower_plus_button = pygame.Rect(self.control_left + 224, 348, 28, 24)
        self.upper_minus_button = pygame.Rect(self.control_left + 190, 384, 28, 24)
        self.upper_plus_button = pygame.Rect(self.control_left + 224, 384, 28, 24)
        self.reset_bounds_button = pygame.Rect(self.control_left, 420, 152, 26)
        self.bounds_table_button = pygame.Rect(self.control_left + 170, 420, 42, 26)
        self.bounds_popup_close_button = pygame.Rect(0, 0, 32, 28)
        self.show_bounds_popup = False

        self.pathway_tab_rects = []
        self.reaction_button_rects = []
        self.flux_tab_rects = []
        self.flux_row_rects = []
        self.results = {}
        self.fluxes = {}

        self.update_sidebar_rects()
        self.update_flux_table_rects()
        self.update_simulation()

    def get_flux_table_layout(self):
        table_left = self.control_left + 600
        table_top = 88
        table_width = max(460, self.screen.get_width() - table_left - 30)
        tab_height = 26
        tab_gap = 7
        row_gap = 5
        selected_reactions = self.pathway_reactions.get(self.selected_flux_tab, [])
        available_height = max(260, self.screen.get_height() - table_top - 24)
        tabs_height = len(self.pathway_reactions) * (tab_height + tab_gap)
        if selected_reactions:
            row_space = available_height - tabs_height - len(selected_reactions) * row_gap
            row_height = max(18, min(30, row_space // len(selected_reactions)))
        else:
            row_height = 22

        return table_left, table_top, table_width, tab_height, row_height, row_gap, tab_gap

    def update_sidebar_rects(self):
        self.pathway_tab_rects = make_pathway_tab_rects(
            self.pathway_reactions,
            self.selected_sidebar_tab,
            self.button_left,
            self.tab_top,
            self.tab_width,
            self.tab_height,
            self.button_height,
            self.button_gap,
        )
        if self.selected_sidebar_tab in self.pathway_reactions:
            self.reaction_button_rects = make_reaction_button_rects(
                self.pathway_reactions,
                self.selected_sidebar_tab,
                self.button_left,
                self.tab_top,
                self.tab_height,
                self.button_width,
                self.button_height,
                self.button_gap,
            )
        else:
            self.reaction_button_rects = []

    def update_flux_table_rects(self):
        table_left, table_top, table_width, tab_height, row_height, row_gap, tab_gap = self.get_flux_table_layout()
        self.flux_tab_rects = []
        self.flux_row_rects = []
        current_y = table_top

        for pathway_name, reaction_names in self.pathway_reactions.items():
            tab_rect = pygame.Rect(table_left, current_y, table_width, tab_height)
            self.flux_tab_rects.append((pathway_name, tab_rect))
            current_y += tab_height + tab_gap

            if pathway_name == self.selected_flux_tab:
                for reaction_name in reaction_names:
                    row_rect = pygame.Rect(table_left + 10, current_y, table_width - 20, row_height)
                    self.flux_row_rects.append((reaction_name, row_rect))
                    current_y += row_height + row_gap

    def run_simulation(self):
        fba_params = engine.copy_reaction_params(self.reaction_params)
        reactions = fba_engine.build_fba_reactions(fba_params)
        if self.use_steady_state_balance:
            balanced_metabolites = fba_engine.make_balanced_metabolites(reactions)
        else:
            balanced_metabolites = None

        return fba_engine.fba_loop(
            reaction_params=self.reaction_params,
            start_slid=self.starting_sliders["glucose"].value,
            atp_start=self.starting_sliders["atp"].value,
            fructose_start=self.starting_sliders["fructose"].value,
            coa_start=self.starting_sliders["coa"].value,
            oxygen_level=self.starting_sliders["oxygen"].value,
            simulation_steps=self.starting_sliders["time"].value,
            balanced_metabolites=balanced_metabolites,
            use_max_flow_bounds=self.use_max_flow_bounds,
            reaction_bounds=self.reaction_bounds,
            objective_reaction_name=self.objective_reaction,
            force_full_respiration=self.force_full_respiration,
            return_fluxes=True,
        )

    def update_simulation(self):
        self.results, self.fluxes = self.run_simulation()

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        if self.show_bounds_popup:
            if self.bounds_popup_close_button.collidepoint(event.pos) or self.bounds_table_button.collidepoint(event.pos):
                self.show_bounds_popup = False
            return None

        if self.home_button.collidepoint(event.pos):
            return "home"

        if self.bounds_table_button.collidepoint(event.pos):
            self.show_bounds_popup = True
            return None

        if self.max_flow_button.collidepoint(event.pos):
            self.use_max_flow_bounds = not self.use_max_flow_bounds
            self.update_simulation()
            return None

        if self.steady_state_button.collidepoint(event.pos):
            self.use_steady_state_balance = not self.use_steady_state_balance
            self.update_simulation()
            return None

        if self.full_respiration_button.collidepoint(event.pos):
            self.force_full_respiration = not self.force_full_respiration
            self.update_simulation()
            return None

        if self.lower_minus_button.collidepoint(event.pos):
            self.adjust_selected_bound("lower", -self.bound_step)
            return None

        if self.lower_plus_button.collidepoint(event.pos):
            self.adjust_selected_bound("lower", self.bound_step)
            return None

        if self.upper_minus_button.collidepoint(event.pos):
            self.adjust_selected_bound("upper", -self.bound_step)
            return None

        if self.upper_plus_button.collidepoint(event.pos):
            self.adjust_selected_bound("upper", self.bound_step)
            return None

        if self.reset_bounds_button.collidepoint(event.pos):
            self.reaction_bounds.pop(self.selected_reaction, None)
            self.update_simulation()
            return None

        for pathway_name, tab_rect in self.pathway_tab_rects:
            if tab_rect.collidepoint(event.pos):
                if pathway_name == self.selected_sidebar_tab:
                    self.selected_sidebar_tab = None
                elif self.pathway_reactions[pathway_name]:
                    self.selected_sidebar_tab = pathway_name
                    self.selected_pathway = pathway_name
                    self.selected_reaction = self.pathway_reactions[self.selected_pathway][0]
                self.update_sidebar_rects()
                return None

        for reaction_name, button_rect in self.reaction_button_rects:
            if button_rect.collidepoint(event.pos):
                self.selected_reaction = reaction_name
                return None

        for pathway_name, tab_rect in self.flux_tab_rects:
            if tab_rect.collidepoint(event.pos):
                self.selected_flux_tab = None if self.selected_flux_tab == pathway_name else pathway_name
                self.update_flux_table_rects()
                return None

        for reaction_name, row_rect in self.flux_row_rects:
            if row_rect.collidepoint(event.pos):
                self.objective_reaction = reaction_name
                self.update_simulation()
                return None

        return None

    def get_selected_bounds(self):
        return self.reaction_bounds.setdefault(
            self.selected_reaction,
            {"lower": 0, "upper": None},
        )

    def adjust_selected_bound(self, bound_name, change):
        bounds = self.get_selected_bounds()
        if bound_name == "lower":
            bounds["lower"] = max(0, bounds.get("lower", 0) + change)
            if bounds.get("upper") is not None:
                bounds["lower"] = min(bounds["lower"], bounds["upper"])
        else:
            current_upper = bounds.get("upper")
            if current_upper is None:
                current_upper = self.reactions_by_name[self.selected_reaction]["max_flow"]
            bounds["upper"] = max(0, current_upper + change)
            bounds["lower"] = min(bounds.get("lower", 0), bounds["upper"])

        self.update_simulation()

    def draw_home_button(self, font):
        theme.draw_button(self.screen, self.home_button, "Home", font)

    def draw_toggle_button(self, button_rect, label, enabled, font):
        theme.draw_button(self.screen, button_rect, label, font, selected=enabled)

    def draw_small_button(self, button_rect, label, font):
        theme.draw_button(self.screen, button_rect, label, font)

    def get_starting_upper_bound(self, reaction_name):
        if not self.use_max_flow_bounds:
            return None
        return self.reactions_by_name[reaction_name]["max_flow"]

    def format_bound(self, value):
        if value is None:
            return "inf"
        return f"{value:.2f}"

    def get_bound_labels(self, reaction_name):
        if reaction_name.endswith("_uptake"):
            return "min uptake", "max uptake"
        if reaction_name.endswith("_export"):
            return "min export", "max export"
        return "min flux", "max flux"

    def get_changed_bounds_rows(self):
        rows = []
        for reaction_name in sorted(self.reaction_bounds):
            bounds = self.reaction_bounds[reaction_name]
            start_lower = 0
            start_upper = self.get_starting_upper_bound(reaction_name)
            current_lower = bounds.get("lower", start_lower)
            current_upper = bounds.get("upper", start_upper)
            if current_lower != start_lower or current_upper != start_upper:
                rows.append((reaction_name, start_lower, current_lower, start_upper, current_upper))
        return rows

    def get_final_flux(self, reaction_name):
        reaction_fluxes = self.fluxes.get(reaction_name, [])
        if not reaction_fluxes:
            return 0

        return reaction_fluxes[-1]

    def draw_flux_table(self, title_font, header_font, row_font):
        table_left, table_top, table_width, tab_height, row_height, row_gap, tab_gap = self.get_flux_table_layout()
        table_top = 50
        title_text = title_font.render("Flux table", True, (20, 36, 32))
        self.screen.blit(title_text, (table_left, table_top))

        for pathway_name, tab_rect in self.flux_tab_rects:
            has_reactions = len(self.pathway_reactions[pathway_name]) > 0
            theme.draw_button(
                self.screen,
                tab_rect,
                pathway_name,
                header_font,
                selected=pathway_name == self.selected_flux_tab,
                enabled=has_reactions,
                align="left",
            )
            if pathway_name == self.selected_flux_tab:
                theme.draw_text(
                    self.screen,
                    "flux",
                    header_font,
                    theme.COLORS["muted"],
                    (tab_rect.right - 12, tab_rect.centery),
                    anchor="midright",
                )

        if self.selected_flux_tab is None:
            return

        for reaction_name, row_rect in self.flux_row_rects:
            if reaction_name == self.objective_reaction:
                pygame.draw.rect(self.screen, theme.COLORS["info_soft"], row_rect, border_radius=4)
                pygame.draw.rect(self.screen, theme.COLORS["info"], row_rect, 1, border_radius=4)

            display_name = reaction_name
            if len(display_name) > 34:
                display_name = display_name[:31] + "..."
            theme.draw_text(self.screen, display_name, row_font, theme.COLORS["text"], (row_rect.x + 6, row_rect.centery), anchor="midleft")
            theme.draw_text(
                self.screen,
                f"{self.get_final_flux(reaction_name):.3f}",
                row_font,
                theme.COLORS["text"],
                (table_left + table_width - 12, row_rect.centery),
                anchor="midright",
            )

    def draw_bounds_popup(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((26, 35, 31, 85))
        self.screen.blit(overlay, (0, 0))

        popup_width = min(820, self.screen.get_width() - 140)
        popup_height = min(500, self.screen.get_height() - 120)
        popup_rect = pygame.Rect(0, 0, popup_width, popup_height)
        popup_rect.center = self.screen.get_rect().center
        theme.draw_panel(self.screen, popup_rect)

        title_font = theme.font(26, bold=True)
        header_font = theme.font(18, bold=True)
        row_font = theme.font(17)
        small_font = theme.font(18)
        theme.draw_text(self.screen, "Changed reaction bounds", title_font, theme.COLORS["text"], (popup_rect.x + 24, popup_rect.y + 34), anchor="midleft")

        self.bounds_popup_close_button = pygame.Rect(popup_rect.right - 48, popup_rect.y + 20, 28, 28)
        theme.draw_button(self.screen, self.bounds_popup_close_button, "x", small_font)

        columns = [
            ("reaction", popup_rect.x + 28, "midleft"),
            ("start min", popup_rect.x + 360, "center"),
            ("current min", popup_rect.x + 460, "center"),
            ("start max", popup_rect.x + 580, "center"),
            ("current max", popup_rect.x + 700, "center"),
        ]
        header_y = popup_rect.y + 82
        for label, x, anchor in columns:
            theme.draw_text(self.screen, label, header_font, theme.COLORS["muted"], (x, header_y), anchor=anchor)

        rows = self.get_changed_bounds_rows()
        if not rows:
            theme.draw_text(
                self.screen,
                "No bounds changed from their starting values.",
                row_font,
                theme.COLORS["muted"],
                popup_rect.center,
            )
            return

        row_top = popup_rect.y + 106
        row_height = 28
        max_rows = max(1, (popup_rect.bottom - row_top - 24) // row_height)
        for index, (reaction_name, start_lower, current_lower, start_upper, current_upper) in enumerate(rows[:max_rows]):
            row_y = row_top + index * row_height
            row_rect = pygame.Rect(popup_rect.x + 20, row_y - 12, popup_rect.width - 40, 24)
            if index % 2 == 0:
                pygame.draw.rect(self.screen, theme.COLORS["surface_alt"], row_rect, border_radius=4)
            display_name = reaction_name if len(reaction_name) <= 32 else reaction_name[:29] + "..."
            theme.draw_text(self.screen, display_name, row_font, theme.COLORS["text"], (popup_rect.x + 28, row_y), anchor="midleft")
            theme.draw_text(self.screen, self.format_bound(start_lower), row_font, theme.COLORS["muted"], (popup_rect.x + 360, row_y))
            theme.draw_text(self.screen, self.format_bound(current_lower), row_font, theme.COLORS["text"], (popup_rect.x + 460, row_y))
            theme.draw_text(self.screen, self.format_bound(start_upper), row_font, theme.COLORS["muted"], (popup_rect.x + 580, row_y))
            theme.draw_text(self.screen, self.format_bound(current_upper), row_font, theme.COLORS["text"], (popup_rect.x + 700, row_y))

        if len(rows) > max_rows:
            hidden_count = len(rows) - max_rows
            theme.draw_text(
                self.screen,
                f"+ {hidden_count} more changed reactions",
                row_font,
                theme.COLORS["muted"],
                (popup_rect.x + 28, popup_rect.bottom - 20),
                anchor="midleft",
            )

    def draw(self):
        self.screen.fill(theme.COLORS["background"])
        title_font = theme.font(34, bold=True)
        label_font = theme.font(22)
        value_font = theme.font(20)
        button_font = theme.font(16)

        self.draw_home_button(label_font)
        title_text = title_font.render("Flux Balance Simulation", True, theme.COLORS["text"])
        self.screen.blit(title_text, (self.control_left, 50))
        self.update_flux_table_rects()

        draw_pathway_tabs(self.screen, self.pathway_tab_rects, self.pathway_reactions, self.selected_sidebar_tab, button_font)
        draw_reaction_buttons(self.screen, self.reaction_button_rects, self.selected_reaction, button_font)

        self.draw_toggle_button(self.max_flow_button, "Use max_flow bounds", self.use_max_flow_bounds, value_font)
        self.draw_toggle_button(self.steady_state_button, "Steady-state balance", self.use_steady_state_balance, value_font)
        self.draw_toggle_button(self.full_respiration_button, "Force full respiration", self.force_full_respiration, value_font)

        objective_text = label_font.render(f"objective: maximize {self.objective_reaction}", True, (0, 0, 0))
        self.screen.blit(objective_text, (self.control_left, 265))

        selected_text = label_font.render(f"bounds reaction: {self.selected_reaction}", True, (0, 0, 0))
        self.screen.blit(selected_text, (self.control_left, 280))

        bounds = self.get_selected_bounds()
        upper_text = "inf" if bounds.get("upper") is None else f"{bounds['upper']:.2f}"
        lower_label, upper_label = self.get_bound_labels(self.selected_reaction)
        lower_line = value_font.render(f"{lower_label}: {bounds.get('lower', 0):.2f}", True, (0, 0, 0))
        upper_line = value_font.render(f"{upper_label}: {upper_text}", True, (0, 0, 0))
        self.screen.blit(lower_line, (self.control_left, 350))
        self.screen.blit(upper_line, (self.control_left, 386))
        self.draw_small_button(self.lower_minus_button, "-", value_font)
        self.draw_small_button(self.lower_plus_button, "+", value_font)
        self.draw_small_button(self.upper_minus_button, "-", value_font)
        self.draw_small_button(self.upper_plus_button, "+", value_font)
        self.draw_small_button(self.reset_bounds_button, "reset bounds", value_font)
        theme.draw_menu_button(self.screen, self.bounds_table_button, selected=self.show_bounds_popup)

        selected_fluxes = self.fluxes.get(self.selected_reaction, [])
        if selected_fluxes:
            flux_lines = [
                f"final flux: {selected_fluxes[-1]:.3f}",
                f"max flux: {max(selected_fluxes):.3f}",
                f"mean flux: {sum(selected_fluxes) / len(selected_fluxes):.3f}",
                f"aerobic ATP: {self.results['aerobic_ATP'][-1]:.3f}",
                f"total ATP: {self.results['Total ATP'][-1]:.3f}",
            ]
        else:
            flux_lines = ["No FBA result available"]

        for i, line in enumerate(flux_lines):
            line_text = value_font.render(line, True, (0, 0, 0))
            self.screen.blit(line_text, (self.control_left, 470 + i * 28))

        self.draw_flux_table(title_font, label_font, button_font)
        if self.show_bounds_popup:
            self.draw_bounds_popup()