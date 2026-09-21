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
    "hexokinase": {"km": 0.075, "max_flow": 2},
    "glucose_6_phosphate_isomerase": {"km": 0.20, "max_flow": 2},
    "glucose_6_phosphate_isomerase_r": {"km": 0.30, "max_flow": 2},
    "phosphofructokinase_1": {"km": 0.50, "max_flow": 2},
    "fructose_biphosphate_aldolase": {"km": 0.075, "max_flow": 1},
    "fructose_biphosphate_aldolase_r": {"km": 1.50, "max_flow": 1},
    "triose_phosphate_isomerase": {"km": 0.45, "max_flow": 1},
    "triose_phosphate_isomerase_r": {"km": 0.30, "max_flow": 1},
    "glyceraldehyde_3_phosphate_dehydrogenase": {"km": 0.006, "max_flow": 1},
    "glyceraldehyde_3_phosphate_dehydrogenase_r": {"km": 0.0008, "max_flow": 1},
    "phosphoglycerate_kinase": {"km": 0.002, "max_flow": 1},
    "phosphoglycerate_kinase_r": {"km": 0.055, "max_flow": 1},
    "phosphoglycerate_mutase": {"km": 0.175, "max_flow": 1},
    "phosphoglycerate_mutase_r": {"km": 0.175, "max_flow": 1},
    "enolase": {"km": 0.125, "max_flow": 1},
    "enolase_r": {"km": 0.125, "max_flow": 1},
    "pyruvate_kinase": {"km": 0.375, "max_flow": 1},
    "pyruvate_energy_yield": {"km": 0.10, "max_flow": 0.5},
}


def copy_reaction_params(reaction_params=None):
    params = {
        name: values.copy()
        for name, values in DEFAULT_REACTION_PARAMS.items()
    }

    if reaction_params is not None:
        for name, values in reaction_params.items():
            if name in params:
                params[name].update(values)

    return params


def reaction_definition(name, reactants, products, params):
    km = params[name]["km"]
    return {
        "name": name,
        "reactants": reactants,
        "products": products,
        "max_flow": params[name]["max_flow"],
        "km": {reactant: km for reactant in reactants},
    }


# computational loop
def comp_loop(reaction_params=None, start_slid=100, atp_start=100):
    params = copy_reaction_params(reaction_params)

    metabolites = {
        "glucose": start_slid,
        "ATP": atp_start,
        "ADP": 0,
        "NAD+": start_slid,
        "NADH": 0,
        "Pi": start_slid,
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

    }

    reactions = [
        reaction_definition("hexokinase", {"glucose": 1, "ATP": 1}, {"G6P": 1, "ADP": 1}, params),
        reaction_definition("glucose_6_phosphate_isomerase", {"G6P": 1}, {"F6P": 1}, params),
        reaction_definition("glucose_6_phosphate_isomerase_r", {"F6P": 1}, {"G6P": 1}, params),
        reaction_definition("phosphofructokinase_1", {"F6P": 1, "ATP": 1}, {"F16BP": 1, "ADP": 1}, params),
        reaction_definition("fructose_biphosphate_aldolase", {"F16BP": 1}, {"DHAP": 1, "G3P": 1}, params),
        reaction_definition("fructose_biphosphate_aldolase_r", {"DHAP": 1, "G3P": 1}, {"F16BP": 1}, params),
        reaction_definition("triose_phosphate_isomerase", {"DHAP": 1}, {"G3P": 1}, params),
        reaction_definition("triose_phosphate_isomerase_r", {"G3P": 1}, {"DHAP": 1}, params),
        reaction_definition("glyceraldehyde_3_phosphate_dehydrogenase", {"G3P": 1, "NAD+": 1, "Pi": 1}, {"13BPG": 1, "NADH": 1}, params),
        reaction_definition("glyceraldehyde_3_phosphate_dehydrogenase_r", {"13BPG": 1, "NADH": 1}, {"G3P": 1, "NAD+": 1, "Pi": 1}, params),
        reaction_definition("phosphoglycerate_kinase", {"13BPG": 1, "ADP": 1}, {"3PG": 1, "ATP": 1}, params),
        reaction_definition("phosphoglycerate_kinase_r", {"3PG": 1, "ATP": 1}, {"13BPG": 1, "ADP": 1}, params),
        reaction_definition("phosphoglycerate_mutase", {"3PG": 1}, {"2PG": 1}, params),
        reaction_definition("phosphoglycerate_mutase_r", {"2PG": 1}, {"3PG": 1}, params),
        reaction_definition("enolase", {"2PG": 1}, {"PEP": 1}, params),
        reaction_definition("enolase_r", {"PEP": 1}, {"2PG": 1}, params),
        reaction_definition("pyruvate_kinase", {"PEP": 1, "ADP": 1}, {"pyruvate": 1, "ATP": 1}, params),
        reaction_definition("pyruvate_energy_yield", {"pyruvate": 1, "ADP": 1}, {"ATP": 32}, params),
    ]

    metabolite_values = {metabolite: [] for metabolite in metabolites}

    for t in time:
        for reaction in reactions:
            apply_reaction(metabolites, reaction, dt)

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




