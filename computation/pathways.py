GLYCOLYSIS_REACTIONS = [
    "hexokinase",
    "glucose_6_phosphate_isomerase",
    "glucose_6_phosphate_isomerase_r",
    "phosphofructokinase_1",
    "fructose_biphosphate_aldolase",
    "fructose_biphosphate_aldolase_r",
    "triose_phosphate_isomerase",
    "triose_phosphate_isomerase_r",
    "glyceraldehyde_3_phosphate_dehydrogenase",
    "glyceraldehyde_3_phosphate_dehydrogenase_r",
    "phosphoglycerate_kinase",
    "phosphoglycerate_kinase_r",
    "phosphoglycerate_mutase",
    "phosphoglycerate_mutase_r",
    "enolase",
    "enolase_r",
    "pyruvate_kinase",
    "pyruvate_energy_yield",
    "lactate_dehydrogenase",
    "mitochondrial_NADH_oxidation",
    "ATP_hydrolysis",
]

CITRIC_ACID_CYCLE_REACTIONS = []
FRUCTOSE_PATHWAY_REACTIONS = [
    "fructokinase",
    "aldolase_B",
    "triose_kinase",
]


def build_pathway_reactions(available_reactions):
    available_reactions = set(available_reactions)
    return {
        "Glycolysis": [
            reaction_name
            for reaction_name in GLYCOLYSIS_REACTIONS
            if reaction_name in available_reactions
        ],
        "Citric acid cycle": [
            reaction_name
            for reaction_name in CITRIC_ACID_CYCLE_REACTIONS
            if reaction_name in available_reactions
        ],
        "Fructose pathways": [
            reaction_name
            for reaction_name in FRUCTOSE_PATHWAY_REACTIONS
            if reaction_name in available_reactions
        ],
    }
