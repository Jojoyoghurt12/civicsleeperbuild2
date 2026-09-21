# Glycolysis Simulator

An interactive Python/Pygame simulator for exploring glycolysis flux dynamics. The project models glycolysis as a simplified reaction network using Michaelis-Menten-like reaction rates, then plots metabolite concentrations over time in an interactive window.

The simulator is intended as an educational systems biology tool rather than a fully quantitative biochemical model.

I got kind of lazy with this one, so bear in mind my horrible coding. Any questions can be sent to j.ten.broeke.1@student.rug.nl

## Features

- Interactive graph of glycolysis metabolites over time
- Reaction buttons for selecting individual glycolysis reactions
- Adjustable `Km` and `max_flow` values per reaction
- Separate starting sliders for glucose and ATP
- Approximate glycolysis `Km` defaults based on literature-style ranges
- Pygame-based interface with metabolite legend and axis labels


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

From the `Flux_dynamics` folder:

```powershell
cd "\your\path\to\the\folder\"
python .\Demo_sliders.py
```

## How It Works

The simulation stores metabolites as concentrations and reactions as dictionaries containing:

- reactants
- products
- `Km`
- `max_flow`

Reaction rates are computed with a simplified Michaelis-Menten saturation term:

```python
rate = max_flow * substrate / (Km + substrate)
```

For reactions with multiple reactants, saturation terms are multiplied together. The simulation then applies each reaction over small timesteps and records metabolite amounts for plotting.

## Biological Scope

This model is biologically inspired, but simplified. It includes glycolysis intermediates, approximate `Km` values, ATP/ADP, NAD+/NADH, phosphate, and a simplified pyruvate-to-ATP yield step.

Some biological details are intentionally simplified or omitted:

- one `Km` value is used per reaction, not per substrate
- reversible reactions are modeled as separate forward/reverse reactions
- detailed allosteric regulation is not included
- the citric acid cycle and electron transport chain are represented by a simplified ATP-yield shortcut

__I will make a second repo with a lot more plausible of a mechanism, however that will be published independently.__

## Dependencies

See [requirements.txt](requirements.txt):

```text
pygame
numpy
matplotlib
```

