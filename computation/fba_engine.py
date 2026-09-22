from scipy.optimize import linprog

try:
    from . import engine
except ImportError:
    from computation import engine


DEFAULT_OBJECTIVE_WEIGHTS = {
    "current_ATP": 1.0,
    "glycolytic_ATP": 1.0,
    "aerobic_ATP": 1.0,
    "GTP": 1.0,
}

DEFAULT_UNBALANCED_METABOLITES = {
    "glycolytic_ATP",
    "anaerobic_ATP",
    "aerobic_ATP",
    "Total ATP",
    "biomass",
}

BIOMASS_DEMAND_REACTION_NAMES = [
    "lipid_biomass_demand",
    "glutamate_family_biomass_demand",
    "heme_methionine_lysine_biomass_demand",
    "aspartate_family_biomass_demand",
]

EXCHANGE_REACTION_NAMES = [
    "glucose_uptake",
    "fructose_uptake",
    "oxygen_uptake",
    "CO2_export",
    "lactate_export",
    "ADP_supply",
    "Pi_supply",
    "ATP_demand",
    "GTP_to_ATP",
    "CoA_regeneration",
]

FULL_RESPIRATION_REACTION_NAMES = [
    "pyruvate_dehydrogenase",
    "citrate_synthase",
    "aconitase",
    "isocitrate_dehydrogenase",
    "alpha_ketoglutarate_dehydrogenase",
    "succinyl_CoA_synthetase",
    "succinate_dehydrogenase",
    "fumarase",
    "malate_dehydrogenase",
    "mitochondrial_NADH_oxidation",
    "mitochondrial_FADH2_oxidation",
]
DEFAULT_FULL_RESPIRATION_MIN_FLUX = 0.1


def make_fba_reaction(name, reactants, products, max_flow):
    return {
        "name": name,
        "reactants": reactants,
        "products": products,
        "max_flow": max_flow,
        "km": {},
        "inhibitors": {},
        "activators": {},
    }


def build_exchange_reactions():
    return [
        make_fba_reaction("glucose_uptake", {}, {"glucose": 1}, 10),
        make_fba_reaction("fructose_uptake", {}, {"fructose": 1}, 0),
        make_fba_reaction("oxygen_uptake", {}, {"O2": 1}, 10),
        make_fba_reaction("CO2_export", {"CO2": 1}, {}, 10),
        make_fba_reaction("lactate_export", {"lactate": 1}, {}, 10),
        make_fba_reaction("ADP_supply", {}, {"ADP": 1}, 100),
        make_fba_reaction("Pi_supply", {}, {"Pi": 1}, 100),
        make_fba_reaction("ATP_demand", {"current_ATP": 1}, {"ADP": 1, "Pi": 1}, 100),
        make_fba_reaction("GTP_to_ATP", {"GTP": 1, "ADP": 1}, {"current_ATP": 1}, 10),
        make_fba_reaction("CoA_regeneration", {"acetyl_CoA": 1}, {"CoA": 1}, 10),
    ]


def build_biomass_demand_reactions():
    return [
        make_fba_reaction("lipid_biomass_demand", {"acetyl_CoA": 1}, {"biomass": 1, "CoA": 1}, 10),
        make_fba_reaction("glutamate_family_biomass_demand", {"alpha_ketoglutarate": 1}, {"biomass": 1}, 10),
        make_fba_reaction("heme_methionine_lysine_biomass_demand", {"succinyl_CoA": 1}, {"biomass": 1, "CoA": 1}, 10),
        make_fba_reaction("aspartate_family_biomass_demand", {"oxaloacetate": 1}, {"biomass": 1}, 10),
    ]


def build_fba_reactions(params):
    reactions = []
    for reaction in engine.build_reactions(params):
        reaction = {
            key: value.copy() if isinstance(value, dict) else value
            for key, value in reaction.items()
        }
        if reaction["name"] in ("mitochondrial_NADH_oxidation", "mitochondrial_FADH2_oxidation"):
            reaction["reactants"]["O2"] = 0.5
            reaction["km"]["O2"] = 0.05
        reactions.append(reaction)

    reactions.extend(build_exchange_reactions())
    reactions.extend(build_biomass_demand_reactions())
    return reactions


def scale_oxygen_dependent_reactions(params, oxygen_level):
    oxygen_level = max(0, min(1, oxygen_level))
    params["mitochondrial_NADH_oxidation"]["max_flow"] *= oxygen_level
    params["mitochondrial_FADH2_oxidation"]["max_flow"] *= oxygen_level


def get_reaction_flux_bound(metabolites, reaction, step_dt, use_max_flow_bounds=True, use_availability_bounds=True):
    upper_bound = reaction["max_flow"] if use_max_flow_bounds else float("inf")
    if use_availability_bounds:
        for reactant, stoich in reaction["reactants"].items():
            if stoich > 0:
                upper_bound = min(upper_bound, metabolites[reactant] / (stoich * step_dt))

    return max(0, upper_bound)


def get_reaction_bounds(metabolites, reaction, step_dt, use_max_flow_bounds=True, reaction_bounds=None, use_availability_bounds=True, force_full_respiration=False, full_respiration_min_flux=DEFAULT_FULL_RESPIRATION_MIN_FLUX):
    configured_bounds = (reaction_bounds or {}).get(reaction["name"], {})
    lower_bound = max(0, configured_bounds.get("lower", 0))
    if force_full_respiration and reaction["name"] in FULL_RESPIRATION_REACTION_NAMES:
        lower_bound = max(lower_bound, full_respiration_min_flux)
    upper_bound = get_reaction_flux_bound(metabolites, reaction, step_dt, use_max_flow_bounds, use_availability_bounds)
    configured_upper = configured_bounds.get("upper")
    if configured_upper is not None:
        upper_bound = min(upper_bound, max(0, configured_upper))

    if lower_bound > upper_bound:
        lower_bound = upper_bound

    return lower_bound, upper_bound


def get_reaction_objective_score(reaction, objective_weights):
    score = 0
    for product, stoich in reaction["products"].items():
        score += objective_weights.get(product, 0) * stoich
    for reactant, stoich in reaction["reactants"].items():
        score -= objective_weights.get(reactant, 0) * stoich

    return score


def build_objective_vector(reactions, objective_weights=None, objective_reaction_name=None):
    if objective_reaction_name is not None:
        return [
            -1 if reaction["name"] == objective_reaction_name else 0
            for reaction in reactions
        ]

    objective_weights = objective_weights or DEFAULT_OBJECTIVE_WEIGHTS
    return [
        -get_reaction_objective_score(reaction, objective_weights)
        for reaction in reactions
    ]


def get_metabolite_names(reactions):
    metabolite_names = set()
    for reaction in reactions:
        metabolite_names.update(reaction["reactants"])
        metabolite_names.update(reaction["products"])

    return sorted(metabolite_names)


def build_stoichiometric_matrix(reactions, balanced_metabolites):
    matrix = []
    for metabolite in balanced_metabolites:
        row = []
        for reaction in reactions:
            produced = reaction["products"].get(metabolite, 0)
            consumed = reaction["reactants"].get(metabolite, 0)
            row.append(produced - consumed)
        matrix.append(row)

    return matrix


def make_balanced_metabolites(reactions, unbalanced_metabolites=None):
    unbalanced_metabolites = unbalanced_metabolites or DEFAULT_UNBALANCED_METABOLITES
    return [
        metabolite
        for metabolite in get_metabolite_names(reactions)
        if metabolite not in unbalanced_metabolites
    ]


def ensure_metabolite_entries(metabolites, reactions):
    for metabolite in get_metabolite_names(reactions):
        metabolites.setdefault(metabolite, 0)


def optimize_fluxes(metabolites, reactions, step_dt=engine.dt, objective_weights=None, balanced_metabolites=None, use_max_flow_bounds=True, reaction_bounds=None, objective_reaction_name=None, use_availability_bounds=True, force_full_respiration=False, full_respiration_min_flux=DEFAULT_FULL_RESPIRATION_MIN_FLUX):
    objective = build_objective_vector(reactions, objective_weights, objective_reaction_name)
    bounds = [
        get_reaction_bounds(metabolites, reaction, step_dt, use_max_flow_bounds, reaction_bounds, use_availability_bounds, force_full_respiration, full_respiration_min_flux)
        for reaction in reactions
    ]

    if balanced_metabolites:
        stoichiometric_matrix = build_stoichiometric_matrix(reactions, balanced_metabolites)
        balance_targets = [0 for metabolite in balanced_metabolites]
    else:
        stoichiometric_matrix = None
        balance_targets = None

    result = linprog(
        c=objective,
        A_eq=stoichiometric_matrix,
        b_eq=balance_targets,
        bounds=bounds,
        method="highs",
    )

    if not result.success:
        return [0 for reaction in reactions]

    return result.x


def apply_fluxes(metabolites, reactions, fluxes, step_dt=engine.dt):
    for reaction, flux in zip(reactions, fluxes):
        for reactant, stoich in reaction["reactants"].items():
            metabolites[reactant] -= stoich * flux * step_dt
            metabolites[reactant] = max(0, metabolites[reactant])

        for product, stoich in reaction["products"].items():
            metabolites[product] += stoich * flux * step_dt


def fba_loop(
    reaction_params=None,
    start_slid=100,
    atp_start=100,
    fructose_start=0,
    coa_start=0.1,
    oxygen_level=1.0,
    simulation_steps=10000,
    objective_weights=None,
    balanced_metabolites=None,
    use_max_flow_bounds=True,
    reaction_bounds=None,
    objective_reaction_name=None,
    force_full_respiration=False,
    full_respiration_min_flux=DEFAULT_FULL_RESPIRATION_MIN_FLUX,
    return_fluxes=False,
):
    params = engine.copy_reaction_params(reaction_params)
    oxygen_level = max(0, min(1, oxygen_level))
    simulation_steps = max(2, int(simulation_steps))
    scale_oxygen_dependent_reactions(params, oxygen_level)

    metabolites = engine.make_initial_metabolites(start_slid, atp_start, fructose_start, coa_start)
    reactions = build_fba_reactions(params)
    ensure_metabolite_entries(metabolites, reactions)
    if objective_reaction_name is None:
        objective_reaction_name = "ATP_demand"
    use_availability_bounds = balanced_metabolites is None
    metabolite_values = {metabolite: [] for metabolite in metabolites}
    flux_values = {reaction["name"]: [] for reaction in reactions}

    for t in range(simulation_steps):
        fluxes = optimize_fluxes(
            metabolites,
            reactions,
            engine.dt,
            objective_weights,
            balanced_metabolites,
            use_max_flow_bounds,
            reaction_bounds,
            objective_reaction_name,
            use_availability_bounds,
            force_full_respiration,
            full_respiration_min_flux,
        )
        apply_fluxes(metabolites, reactions, fluxes, engine.dt)

        metabolites["anaerobic_ATP"] = metabolites["glycolytic_ATP"] * (1 - oxygen_level)
        metabolites["Total ATP"] = atp_start + metabolites["glycolytic_ATP"] + metabolites["aerobic_ATP"]

        for metabolite, value in metabolites.items():
            metabolite_values[metabolite].append(value)
        for reaction, flux in zip(reactions, fluxes):
            flux_values[reaction["name"]].append(float(flux))

    if return_fluxes:
        return metabolite_values, flux_values

    return metabolite_values