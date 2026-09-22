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
        self.lower_minus_button = pygame.Rect(self.control_left + 90, 348, 28, 24)
        self.lower_plus_button = pygame.Rect(self.control_left + 124, 348, 28, 24)
        self.upper_minus_button = pygame.Rect(self.control_left + 90, 384, 28, 24)
        self.upper_plus_button = pygame.Rect(self.control_left + 124, 384, 28, 24)
        self.reset_bounds_button = pygame.Rect(self.control_left, 420, 152, 26)

        self.pathway_tab_rects = []
        self.reaction_button_rects = []
        self.flux_tab_rects = []
        self.flux_row_rects = []
        self.results = {}
        self.fluxes = {}

        self.update_sidebar_rects()
        self.update_flux_table_rects()
        self.update_simulation()

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
        table_left = self.control_left + 640
        table_top = 88
        table_width = 420
        tab_height = 24
        row_height = 20
        row_gap = 4
        tab_gap = 6
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

        if self.home_button.collidepoint(event.pos):
            return "home"

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
                    self.objective_reaction = self.selected_reaction
                    self.update_simulation()
                self.update_sidebar_rects()
                return None

        for reaction_name, button_rect in self.reaction_button_rects:
            if button_rect.collidepoint(event.pos):
                self.selected_reaction = reaction_name
                self.objective_reaction = reaction_name
                self.update_simulation()
                return None

        for pathway_name, tab_rect in self.flux_tab_rects:
            if tab_rect.collidepoint(event.pos):
                self.selected_flux_tab = None if self.selected_flux_tab == pathway_name else pathway_name
                self.update_flux_table_rects()
                return None

        for reaction_name, row_rect in self.flux_row_rects:
            if row_rect.collidepoint(event.pos):
                self.selected_reaction = reaction_name
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
        pygame.draw.rect(self.screen, (230, 235, 232), self.home_button)
        pygame.draw.rect(self.screen, (30, 45, 42), self.home_button, 1)
        button_text = font.render("Home", True, (20, 36, 32))
        self.screen.blit(
            button_text,
            (
                self.home_button.centerx - button_text.get_width() // 2,
                self.home_button.centery - button_text.get_height() // 2,
            )
        )

    def draw_toggle_button(self, button_rect, label, enabled, font):
        fill_color = (190, 220, 190) if enabled else (230, 230, 230)
        pygame.draw.rect(self.screen, fill_color, button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 1)
        button_text = font.render(label, True, (0, 0, 0))
        self.screen.blit(
            button_text,
            (
                button_rect.centerx - button_text.get_width() // 2,
                button_rect.centery - button_text.get_height() // 2,
            )
        )

    def draw_small_button(self, button_rect, label, font):
        pygame.draw.rect(self.screen, (230, 230, 230), button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 1)
        button_text = font.render(label, True, (0, 0, 0))
        self.screen.blit(
            button_text,
            (
                button_rect.centerx - button_text.get_width() // 2,
                button_rect.centery - button_text.get_height() // 2,
            )
        )

    def get_final_flux(self, reaction_name):
        reaction_fluxes = self.fluxes.get(reaction_name, [])
        if not reaction_fluxes:
            return 0

        return reaction_fluxes[-1]

    def draw_flux_table(self, title_font, header_font, row_font):
        table_left = self.control_left + 640
        table_top = 50
        table_width = 420
        title_text = title_font.render("Flux table", True, (20, 36, 32))
        self.screen.blit(title_text, (table_left, table_top))

        for pathway_name, tab_rect in self.flux_tab_rects:
            has_reactions = len(self.pathway_reactions[pathway_name]) > 0
            if pathway_name == self.selected_flux_tab:
                fill_color = (210, 230, 255)
            elif has_reactions:
                fill_color = (235, 235, 235)
            else:
                fill_color = (225, 225, 225)

            pygame.draw.rect(self.screen, fill_color, tab_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), tab_rect, 1)
            tab_text = header_font.render(pathway_name, True, (0, 0, 0) if has_reactions else (120, 120, 120))
            self.screen.blit(tab_text, (tab_rect.x + 8, tab_rect.centery - tab_text.get_height() // 2))

        if self.selected_flux_tab is None:
            return

        value_header = header_font.render("flux", True, (0, 0, 0))
        self.screen.blit(value_header, (table_left + table_width - 62, self.flux_row_rects[0][1].y - 22 if self.flux_row_rects else table_top + 40))

        for reaction_name, row_rect in self.flux_row_rects:
            if reaction_name == self.selected_reaction:
                pygame.draw.rect(self.screen, (220, 235, 255), row_rect)
                pygame.draw.rect(self.screen, (60, 110, 180), row_rect, 1)

            display_name = reaction_name
            if len(display_name) > 34:
                display_name = display_name[:31] + "..."
            name_text = row_font.render(display_name, True, (0, 0, 0))
            flux_text = row_font.render(f"{self.get_final_flux(reaction_name):.3f}", True, (0, 0, 0))
            self.screen.blit(name_text, (row_rect.x + 4, row_rect.y + 2))
            self.screen.blit(flux_text, (table_left + table_width - flux_text.get_width() - 12, row_rect.y + 2))

    def draw(self):
        self.screen.fill((245, 245, 245))
        title_font = pygame.font.SysFont(None, 36)
        label_font = pygame.font.SysFont(None, 24)
        value_font = pygame.font.SysFont(None, 22)
        button_font = pygame.font.SysFont(None, 18)

        self.draw_home_button(label_font)
        title_text = title_font.render("Flux Balance Simulation", True, (20, 36, 32))
        self.screen.blit(title_text, (self.control_left, 50))
        self.update_flux_table_rects()

        draw_pathway_tabs(self.screen, self.pathway_tab_rects, self.pathway_reactions, self.selected_sidebar_tab, button_font)
        draw_reaction_buttons(self.screen, self.reaction_button_rects, self.selected_reaction, button_font)

        self.draw_toggle_button(self.max_flow_button, "Use max_flow bounds", self.use_max_flow_bounds, value_font)
        self.draw_toggle_button(self.steady_state_button, "Steady-state balance", self.use_steady_state_balance, value_font)
        self.draw_toggle_button(self.full_respiration_button, "Force full respiration", self.force_full_respiration, value_font)

        objective_text = label_font.render(f"objective: maximize {self.objective_reaction}", True, (0, 0, 0))
        self.screen.blit(objective_text, (self.control_left, 265))

        selected_text = label_font.render(f"selected reaction: {self.selected_reaction}", True, (0, 0, 0))
        self.screen.blit(selected_text, (self.control_left, 280))

        bounds = self.get_selected_bounds()
        upper_text = "inf" if bounds.get("upper") is None else f"{bounds['upper']:.2f}"
        lower_line = value_font.render(f"lower bound: {bounds.get('lower', 0):.2f}", True, (0, 0, 0))
        upper_line = value_font.render(f"upper bound: {upper_text}", True, (0, 0, 0))
        self.screen.blit(lower_line, (self.control_left, 350))
        self.screen.blit(upper_line, (self.control_left, 386))
        self.draw_small_button(self.lower_minus_button, "-", value_font)
        self.draw_small_button(self.lower_plus_button, "+", value_font)
        self.draw_small_button(self.upper_minus_button, "-", value_font)
        self.draw_small_button(self.upper_plus_button, "+", value_font)
        self.draw_small_button(self.reset_bounds_button, "reset bounds", value_font)

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