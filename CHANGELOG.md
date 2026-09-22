# Changelog


## 1.0.1

- Refined the overall simulator UI styling with a shared theme system.
- Updated the home screen with themed mode buttons, a red exit button, and fullscreen toggle support with `F11` and the enlarging button.
- Improved the Kinetics simulator layout and styling:
    - themed graph panel, axes, gridlines, sliders, legend, and status text
    - smaller slider knobs and better slider label spacing
    - improved legend row alignment and selected-reaction emphasis
- Improved the Flux Balance Analysis:
    - separated objective selection from bound editing (bug)
    - flux table rows now set the FBA objective (bug)
    - left reaction list now selects the reaction whose bounds can be edited
    - added a changed-bounds popup table with a menu button as well as a reset button
    - improved bound labels for uptake/export/internal reactions
- Updated FBA model defaults and reactions:
    - fructose uptake now defaults to closed
    - added reverse reaction options for lactate dehydrogenase and selected TCA reactions
    - added `aconitase_r`, `fumarase_r`, `malate_dehydrogenase_r`, `succinyl_CoA_synthetase_r`, and `lactate_dehydrogenase_r`
- Added app icon support for the installer/app build workflow.
- Updated installer metadata and output filename for version `1.0.1`.


## 1.0.0

- First public release
- includes:
    - FBA (Flux Balance Analysis)
    - Kinetic simulator
        - With adjustable Km values and max flows
- Added Biomass precursor demand objectives 
    