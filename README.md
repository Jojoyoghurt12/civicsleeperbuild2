# Glycolysis Simulator

An interactive Python/Pygame simulator for exploring glycolysis flux dynamics. The project models glycolysis as a simplified reaction network using Michaelis-Menten-like reaction rates, then plots metabolite concentrations over time in an interactive window.

The simulator is intended as an educational systems biology tool rather than a fully quantitative biochemical model.

I got kind of lazy with this one, so bear in mind my horrible coding. Any questions can be sent to j.ten.broeke.1@student.rug.nl

## Features

- Interactive graph of glycolysis metabolites over time
- Pathway tabs for grouping reaction buttons
- Reaction buttons for selecting individual reactions
- Adjustable substrate-specific `Km` values and `max_flow` values per reaction
- Starting sliders for glucose and initial ATP
- Oxygen slider for aerobic versus anaerobic-like conditions
- Time slider for changing the simulation length
- Toggleable and highlightable metabolite curves
- Approximate glycolysis `Km` defaults based on literature-style ranges
- Pygame-based interface with metabolite legend and axis labels

## Project Structure

```text
Flux_dynamics_expansion/
	Demo_sliders.py
	README.md
	requirements.txt

	computation/
		__init__.py
		engine.py
		pathways.py

	ui/
		__init__.py
		sliders.py
		graph.py
		controls.py
```

### What Goes Where

[Demo_sliders.py](Demo_sliders.py) is the main Pygame program. It opens the window, owns the event loop, connects user input to the simulation, and calls the drawing/helper functions from the `ui` package.

[computation/engine.py](computation/engine.py) contains the simulation engine. This is where metabolites, reaction parameters, Michaelis-Menten-like rates, regulation, oxygen-dependent ATP production, lactate production, ATP hydrolysis, and the main `comp_loop(...)` function live.

[computation/pathways.py](computation/pathways.py) contains pathway groupings for the reaction buttons. Currently, the active pathway is glycolysis. Empty placeholder groups are already present for the citric acid cycle and fructose pathways.

[ui/sliders.py](ui/sliders.py) contains the reusable `Slider` class and the helper for building substrate-specific `Km` sliders.

[ui/graph.py](ui/graph.py) contains graph-related code: curve creation, max-value scaling, axes, curve drawing, the clickable metabolite legend, and the thicker/highlighted `Total ATP` curve behavior.

[ui/controls.py](ui/controls.py) contains UI control helpers: step buttons, pathway tabs, reaction buttons, `Km` increment/decrement buttons, and the `Total ATP` toggle button.


## Installation

Create and activate a virtual environment, then install the required packages:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If your PowerShell execution policy blocks activation, you can run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Running The Simulator

From the `Flux_dynamics_expansion` folder:

```powershell
cd "\your\path\to\the\folder\"
python .\Demo_sliders.py
```

## How It Works

The simulation stores metabolites as concentrations and reactions as dictionaries containing:

- reactants
- products
- substrate-specific `Km` values
- `max_flow`
- optional inhibitors
- optional activators

Reaction rates are computed with a simplified Michaelis-Menten saturation term:

```python
rate = max_flow * substrate / (Km + substrate)
```

For reactions with multiple reactants, saturation terms are multiplied together. The simulation then applies each reaction over small timesteps and records metabolite amounts for plotting.

The UI reads the returned metabolite time series and draws each metabolite as a curve. Legend entries can be clicked to highlight a metabolite curve. `Total ATP` can also be toggled with its own button.

## Biological Scope

This model is biologically inspired, but simplified. It includes glycolysis intermediates, approximate substrate-specific `Km` values, current ATP/ADP, NAD+/NADH, phosphate, lactate, oxygen-dependent pyruvate energy yield, mitochondrial NADH oxidation, and ATP hydrolysis for ADP recycling.

Some biological details are intentionally simplified or omitted:

- rates are simplified and are not fitted to experimental kinetic data
- reversible reactions are modeled as separate forward/reverse reactions
- allosteric regulation is simplified
- the citric acid cycle and electron transport chain are represented by a simplified ATP-yield shortcut
- fructose metabolism is not implemented yet, but the UI has a placeholder pathway tab for it

The current structure is meant to make it easier to add fructose metabolism, the citric acid cycle, and a more explicit electron transport chain later.

## Dependencies

See [requirements.txt](requirements.txt):

```text
pygame
numpy
matplotlib
```

