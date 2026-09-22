import matplotlib.pyplot as plt

# metabolites

# set up reactions
'''
dX/dt = 1 * fr_startX - 1 * fr_XY
...

See table i made in excel and reaction scheme in reactions.md
'''

# flow rates

'''
Maybe cool to let them depend on availability

add a chance of interaction based on the availability of the metabolites needed

'''
# Michaelis-Menten-like rate function for one substrate.
def michaelis_menten_saturation(available, km):
    if available <= 0:
        return 0
    return available / (km + available)


def reaction_rate(metabolites, reaction):
    rate = reaction["max_flow"]

    for reactant in reaction["reactants"]:
        rate *= michaelis_menten_saturation(
            metabolites[reactant],
            reaction["km"][reactant]
        )

    for inhibitor, ki in reaction.get("inhibitors", {}).items():
        rate *= ki / (ki + metabolites[inhibitor])

    for activator, ka in reaction.get("activators", {}).items():
        rate *= metabolites[activator] / (ka + metabolites[activator])

    return rate


def apply_reaction(metabolites, reaction, dt):
    rate = reaction_rate(metabolites, reaction)

    for reactant, stoich in reaction["reactants"].items():
        rate = min(rate, metabolites[reactant] / (stoich * dt))

    for reactant, stoich in reaction["reactants"].items():
        metabolites[reactant] -= stoich * rate * dt

    for product, stoich in reaction["products"].items():
        metabolites[product] += stoich * rate * dt

    return rate

# initialize lists to store values over time


time = range(10000)
dt = 0.01

DEFAULT_REACTION_PARAMS = {
    "hexokinase": {"km": {"glucose": 0.075, "current_ATP": 0.10}, "max_flow": 2},
    "glucose_6_phosphate_isomerase": {"km": {"G6P": 0.20}, "max_flow": 2},
    "glucose_6_phosphate_isomerase_r": {"km": {"F6P": 0.30}, "max_flow": 2},
    "phosphofructokinase_1": {"km": {"F6P": 0.50, "current_ATP": 0.10}, "max_flow": 2},
    "fructose_biphosphate_aldolase": {"km": {"F16BP": 0.075}, "max_flow": 1},
    "fructose_biphosphate_aldolase_r": {"km": {"DHAP": 2.00, "G3P": 1.00}, "max_flow": 1},
    "triose_phosphate_isomerase": {"km": {"DHAP": 0.45}, "max_flow": 1},
    "triose_phosphate_isomerase_r": {"km": {"G3P": 0.30}, "max_flow": 1},
    "glyceraldehyde_3_phosphate_dehydrogenase": {"km": {"G3P": 0.006, "NAD+": 0.05, "Pi": 1.00}, "max_flow": 1},
    "glyceraldehyde_3_phosphate_dehydrogenase_r": {"km": {"13BPG": 0.0008, "NADH": 0.01}, "max_flow": 0.05},
    "phosphoglycerate_kinase": {"km": {"13BPG": 0.002, "ADP": 0.10}, "max_flow": 1},
    "phosphoglycerate_kinase_r": {"km": {"3PG": 0.055, "current_ATP": 0.10}, "max_flow": 0.05},
    "phosphoglycerate_mutase": {"km": {"3PG": 0.175}, "max_flow": 1},
    "phosphoglycerate_mutase_r": {"km": {"2PG": 0.175}, "max_flow": 0.05},
    "enolase": {"km": {"2PG": 0.125}, "max_flow": 1},
    "enolase_r": {"km": {"PEP": 0.125}, "max_flow": 0.05},
    "pyruvate_kinase": {"km": {"PEP": 0.375, "ADP": 0.30}, "max_flow": 1},
    "pyruvate_energy_yield": {"km": {"pyruvate": 0.10, "ADP": 0.30, "Pi": 1.00}, "max_flow": 0.5},
    "lactate_dehydrogenase": {"km": {"pyruvate": 0.10, "NADH": 0.01}, "max_flow": 1},
    "mitochondrial_NADH_oxidation": {"km": {"NADH": 0.05}, "max_flow": 2},
    "ATP_hydrolysis": {"km": {"current_ATP": 1.00}, "max_flow": 0.3},
    "fructokinase": {"km": {"fructose": 0.50, "current_ATP": 0.10}, "max_flow": 1},
    "aldolase_B": {"km": {"F1P": 0.20}, "max_flow": 1},
    "triose_kinase": {"km": {"glyceraldehyde": 0.30, "current_ATP": 0.10}, "max_flow": 1},
}


def copy_reaction_params(reaction_params=None):
    params = {
        name: {
            key: value.copy() if isinstance(value, dict) else value
            for key, value in values.items()
        }
        for name, values in DEFAULT_REACTION_PARAMS.items()
    }

    if reaction_params is not None:
        for name, values in reaction_params.items():
            if name in params:
                params[name].update(values)

    return params


def get_reaction_km_value(reaction_params, reaction_name):
    km = reaction_params[reaction_name]["km"]
    if isinstance(km, dict):
        return sum(km.values()) / len(km)

    return km


def set_reaction_km_value(reaction_params, reaction_name, value):
    km = reaction_params[reaction_name]["km"]
    if isinstance(km, dict):
        for reactant in km:
            km[reactant] = value
    else:
        reaction_params[reaction_name]["km"] = value


def set_reaction_substrate_km_value(reaction_params, reaction_name, substrate, value):
    km = reaction_params[reaction_name]["km"]
    if isinstance(km, dict):
        km[substrate] = value
    else:
        reaction_params[reaction_name]["km"] = value


def reaction_definition(name, reactants, products, params, inhibitors=None, activators=None):
    km = params[name]["km"]
    if isinstance(km, dict):
        km_by_reactant = {
            reactant: km.get(reactant, get_reaction_km_value(params, name))
            for reactant in reactants
        }
    else:
        km_by_reactant = {reactant: km for reactant in reactants}

    return {
        "name": name,
        "reactants": reactants,
        "products": products,
        "max_flow": params[name]["max_flow"],
        "km": km_by_reactant,
        "inhibitors": inhibitors or {},
        "activators": activators or {},
    }


def build_reactions(params):
    return [
        reaction_definition("hexokinase", {"glucose": 1, "current_ATP": 1}, {"G6P": 1, "ADP": 1}, params, inhibitors={"G6P": 0.2}),
        reaction_definition("glucose_6_phosphate_isomerase", {"G6P": 1}, {"F6P": 1}, params),
        reaction_definition("glucose_6_phosphate_isomerase_r", {"F6P": 1}, {"G6P": 1}, params),
        reaction_definition("phosphofructokinase_1", {"F6P": 1, "current_ATP": 1}, {"F16BP": 1, "ADP": 1}, params, inhibitors={"current_ATP": 2.0}, activators={"ADP": 0.5}),
        reaction_definition("fructose_biphosphate_aldolase", {"F16BP": 1}, {"DHAP": 1, "G3P": 1}, params),
        reaction_definition("fructose_biphosphate_aldolase_r", {"DHAP": 1, "G3P": 1}, {"F16BP": 1}, params),
        reaction_definition("triose_phosphate_isomerase", {"DHAP": 1}, {"G3P": 1}, params),
        reaction_definition("triose_phosphate_isomerase_r", {"G3P": 1}, {"DHAP": 1}, params),
        reaction_definition("glyceraldehyde_3_phosphate_dehydrogenase", {"G3P": 1, "NAD+": 1, "Pi": 1}, {"13BPG": 1, "NADH": 1}, params, inhibitors={"NADH": 5.0}),
        reaction_definition("glyceraldehyde_3_phosphate_dehydrogenase_r", {"13BPG": 1, "NADH": 1}, {"G3P": 1, "NAD+": 1, "Pi": 1}, params),
        reaction_definition("phosphoglycerate_kinase", {"13BPG": 1, "ADP": 1}, {"3PG": 1, "current_ATP": 1, "glycolytic_ATP": 1}, params),
        reaction_definition("phosphoglycerate_kinase_r", {"3PG": 1, "current_ATP": 1}, {"13BPG": 1, "ADP": 1}, params),
        reaction_definition("phosphoglycerate_mutase", {"3PG": 1}, {"2PG": 1}, params),
        reaction_definition("phosphoglycerate_mutase_r", {"2PG": 1}, {"3PG": 1}, params),
        reaction_definition("enolase", {"2PG": 1}, {"PEP": 1}, params),
        reaction_definition("enolase_r", {"PEP": 1}, {"2PG": 1}, params),
        reaction_definition("pyruvate_kinase", {"PEP": 1, "ADP": 1}, {"pyruvate": 1, "current_ATP": 1, "glycolytic_ATP": 1}, params, inhibitors={"current_ATP": 2.0}, activators={"F16BP": 0.1}),
        reaction_definition("pyruvate_energy_yield", {"pyruvate": 1, "ADP": 15, "Pi": 15}, {"current_ATP": 15, "aerobic_ATP": 15}, params),
        reaction_definition("lactate_dehydrogenase", {"pyruvate": 1, "NADH": 1}, {"lactate": 1, "NAD+": 1}, params, inhibitors={"NAD+": 0.5}),
        reaction_definition("mitochondrial_NADH_oxidation", {"NADH": 1}, {"NAD+": 1}, params),
        reaction_definition("ATP_hydrolysis", {"current_ATP": 1}, {"ADP": 1, "Pi": 1}, params),
        reaction_definition("fructokinase", {"fructose": 1, "current_ATP": 1}, {"F1P": 1, "ADP": 1}, params),
        reaction_definition("aldolase_B", {"F1P": 1}, {"DHAP": 1, "glyceraldehyde": 1}, params),
        reaction_definition("triose_kinase", {"glyceraldehyde": 1, "current_ATP": 1}, {"G3P": 1, "ADP": 1}, params),
    ]


# computational loop
def comp_loop(reaction_params=None, start_slid=100, atp_start=100, fructose_start=0, oxygen_level=1.0, simulation_steps=10000):
    params = copy_reaction_params(reaction_params)
    oxygen_level = max(0, min(1, oxygen_level))
    simulation_steps = max(2, int(simulation_steps))
    params["pyruvate_energy_yield"]["max_flow"] *= oxygen_level
    params["mitochondrial_NADH_oxidation"]["max_flow"] *= oxygen_level

    metabolites = {
        "glucose": start_slid,
        "fructose": fructose_start,
        "current_ATP": atp_start,
        "ADP": max(0.1, atp_start * 0.25),
        "glycolytic_ATP": 0,
        "anaerobic_ATP": 0,
        "aerobic_ATP": 0,
        "NAD+": max(0.1, start_slid * 0.2),
        "NADH": max(0.01, start_slid * 0.02),
        "Pi": max(1.0, start_slid * 2.0),
        "G6P": 0,
        "F6P": 0,
        "F16BP": 0,
        "DHAP": 0,
        "G3P": 0,
        "13BPG": 0,
        "3PG": 0,
        "2PG": 0,
        "PEP": 0,
        "pyruvate": 0,
        "lactate": 0,
        "F1P": 0,
        "glyceraldehyde": 0,
        "Total ATP": atp_start,

    }

    reactions = build_reactions(params)

    metabolite_values = {metabolite: [] for metabolite in metabolites}

    for t in range(simulation_steps):
        for reaction in reactions:
            apply_reaction(metabolites, reaction, dt)

        metabolites["anaerobic_ATP"] = metabolites["glycolytic_ATP"] * (1 - oxygen_level)
        metabolites["Total ATP"] = atp_start + metabolites["glycolytic_ATP"] + metabolites["aerobic_ATP"]

        for metabolite, value in metabolites.items():
            metabolite_values[metabolite].append(value)

    return metabolite_values



# plot the results over time
if __name__ == "__main__":
    metabolite_values = comp_loop(start_slid=10, atp_start=2)
    for metabolite, values in metabolite_values.items():
        plt.plot(time, values, label=metabolite)

    plt.xlabel("Time")
    plt.ylabel("Amount")
    plt.legend()
    plt.show()




