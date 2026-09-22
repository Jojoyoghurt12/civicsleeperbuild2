# Systems Biology Simulator

An interactive Python/Pygame simulator for exploring central carbon metabolism with two complementary modes:

- a dynamic kinetics-style simulation of glycolysis, fructose metabolism, the TCA cycle, redox carriers, and ATP production
- a Flux Balance Analysis simulation for maximizing ATP demand, respiratory flux, exchange reactions, or biomass precursor demand

The simulator is intended as an educational systems biology tool. It is biologically inspired, but it is not a fully quantitative biochemical model.

Questions can be sent to j.ten.broeke.1@student.rug.nl.

## Features

### App Navigation

- Home screen with separate entry points for `Kinetics sim` and `Flux Balance sim`
- Shared reaction/pathway definitions between the kinetic and FBA views
- Pygame-based interactive interface

### Kinetics Simulation

- Interactive graph of metabolite concentrations over time
- Pathway tabs for glycolysis, citric acid cycle, and fructose pathways
- Reaction buttons for selecting individual reactions
- Adjustable substrate-specific `Km` values and `max_flow` values per reaction
- Starting sliders for glucose, fructose, ATP, CoA, oxygen, and simulation time
- Toggleable and highlightable metabolite curves
- Explicit metabolite tracking for ATP, ADP, Pi, NAD+/NADH, FAD/FADH2, GTP, CO2, lactate, and TCA intermediates
- Oxygen-dependent mitochondrial NADH and FADH2 oxidation
- Modern ATP yield assumptions:
  - NADH produces approximately `2.5 ATP`
  - FADH2 produces approximately `1.5 ATP`

### Flux Balance Simulation

- Linear-programming FBA solver using `scipy.optimize.linprog`
- Steady-state mass-balance mode using `S v = 0`
- Steady-state balance is enabled by default
- COBRA-like reaction bounds:
  - lower bound controls
  - upper bound controls
  - reset bounds button
  - optional `max_flow` upper bounds
- Objective reaction selection by clicking a reaction or flux-table row
- Default objective: maximize `ATP_demand`
- Exchange reactions for glucose, fructose, oxygen, CO2, lactate, ADP, Pi, ATP demand, GTP-to-ATP conversion, and CoA regeneration
- Flux table with pathway accordions and final flux values
- `Force full respiration` toggle enabled by default
- Forced respiration applies a minimum flux through:
  - pyruvate dehydrogenase
  - the TCA cycle
  - mitochondrial NADH oxidation
  - mitochondrial FADH2 oxidation

### Biomass Demand Objectives

The FBA mode includes a simplified `biomass` metabolite and four biomass precursor demand reactions. These let the model focus on producing biosynthetic branch-point precursors instead of only maximizing ATP.

| Demand reaction | Precursor consumed | Biological interpretation |
| --- | --- | --- |
| `lipid_biomass_demand` | `acetyl_CoA` | lipids, fatty acids, cholesterol, leucine-related precursor demand |
| `glutamate_family_biomass_demand` | `alpha_ketoglutarate` | glutamate, glutamine, arginine, and proline family precursor demand |
| `heme_methionine_lysine_biomass_demand` | `succinyl_CoA` | heme/tetrapyrrole, methionine, and lysine-related precursor demand |
| `aspartate_family_biomass_demand` | `oxaloacetate` | aspartate family amino acids and nucleotide precursor demand |

In steady-state FBA, `biomass` is intentionally left unbalanced so these demand reactions can act as objectives.

## Project Structure

```text
Flux_dynamics_expansion/
    Demo_sliders.py
    README.md
    requirements.txt

    computation/
        __init__.py
        engine.py
        fba_engine.py
        pathways.py

    ui/
        __init__.py
        controls.py
        fba_screen.py
        graph.py
        sliders.py
```

## What Goes Where

[Demo_sliders.py](Demo_sliders.py) is the main Pygame program. It opens the window, owns the event loop, shows the home screen, and routes between the kinetics and FBA modes.

[computation/engine.py](computation/engine.py) contains the kinetic simulation engine. This is where metabolites, reaction parameters, Michaelis-Menten-like rates, regulation, oxygen-dependent ATP production, lactate production, ATP hydrolysis, TCA reactions, and the main `comp_loop(...)` function live.

[computation/fba_engine.py](computation/fba_engine.py) contains the FBA model and solver. It builds FBA-compatible reactions, adds exchange and biomass demand reactions, creates steady-state constraints, applies reaction bounds, and runs `linprog`.

[computation/pathways.py](computation/pathways.py) contains pathway groupings for reaction accordions.

[ui/fba_screen.py](ui/fba_screen.py) contains the FBA user interface, including objective selection, bounds controls, steady-state/full-respiration toggles, and the flux table.

[ui/sliders.py](ui/sliders.py) contains the reusable `Slider` class and the helper for building substrate-specific `Km` sliders.

[ui/graph.py](ui/graph.py) contains graph-related code: curve creation, max-value scaling, axes, curve drawing, the clickable metabolite legend, and highlighted metabolite behavior.

[ui/controls.py](ui/controls.py) contains UI control helpers: step buttons, pathway tabs, reaction buttons, and increment/decrement controls.

## Installation

Create and activate a virtual environment, then install the required packages:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If your PowerShell execution policy blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Running The Simulator

From the `Flux_dynamics_expansion` folder:

```powershell
cd "\your\path\to\Flux_dynamics_expansion"
python .\Demo_sliders.py
```

## How The Kinetic Mode Works

The kinetic simulation stores metabolites as concentrations and reactions as dictionaries containing:

- reactants
- products
- substrate-specific `Km` values
- `max_flow`
- optional inhibitors
- optional activators

Reaction rates are computed with simplified Michaelis-Menten-like saturation terms:

```python
rate = max_flow * substrate / (Km + substrate)
```

For reactions with multiple reactants, saturation terms are multiplied together. The simulation applies each reaction over small timesteps and records metabolite amounts for plotting.

## How The FBA Mode Works

The FBA mode treats each reaction as a flux variable. When steady-state mode is enabled, it builds a stoichiometric matrix and solves:

```text
S v = 0
```

The selected objective reaction is maximized. For example:

- selecting `ATP_demand` maximizes ATP usage/production capacity
- selecting `aspartate_family_biomass_demand` maximizes oxaloacetate diversion into biomass
- selecting `glutamate_family_biomass_demand` maximizes alpha-ketoglutarate diversion into biomass

The solver uses bounds from reaction `max_flow` values, user-edited lower/upper bounds, and optional full-respiration minimum flux constraints.

## Biological Scope And Simplifications

This model is simplified on purpose. It is useful for learning pathway logic, flux tradeoffs, and the difference between kinetic simulation and constraint-based FBA, but it should not be interpreted as a quantitatively calibrated cell model.

Important simplifications include:

- rates are not fitted to experimental kinetic data
- reversible reactions are represented as separate forward and reverse reactions
- allosteric regulation is simplified
- oxidative phosphorylation is represented by direct NADH/FADH2 ATP-yield reactions
- biomass demand reactions are coarse precursor drains, not full biomass equations
- lactate production is allowed as a normal pyruvate fate unless constrained by the selected objective or bounds
- full respiration currently forces respiratory pathway usage, but does not by itself guarantee that every glucose-derived carbon atom is fully oxidized

## Dependencies

See [requirements.txt](requirements.txt):

```text
pygame
numpy
matplotlib
scipy
```
