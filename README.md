# gprMax-Designer
A GUI front-end for gprMax 3 - simulation program used in GPR method created by Giannopoulos and Warren (https://github.com/gprMax/gprMax). 

This program is being developed as a master thesis on AGH University of Science and Technology in Kraków, Faculty of Geology, Geophysics and Environmental Protection.

Author: Tomasz Siwek (tsiwek@g.pl)

Supervisor: dr inż. (Ph. D.) Jerzy Karczewski, Department of Geophysics

# 996 ICU
If you liked my project, give those guys a star and spread awareness: https://github.com/996icu/996.ICU.

[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)

# Installation
1. Make sure to have Python 3 (ver >= 3.6) and Anaconda installed. If you do not wish to use separate environment, make sure to install with `pip` all dependencies listed in `conda_env.yml`.
2. Clone repository to the directory of your choosing.
3. Create Anaconda environment using `.yml` file that is shipped with the program: `conda env create -f conda_env.yml`.

# Usage
1. Activate conda environment with: `conda activate gprMaxDesigner` in main project directory.
2. Run program: `python main.pyw`.
3. There are 4 basic shapes you can draw into your model: boxes, cylinders, cylindrical sectors, and polygons. Choose desired shape type from RMB popup or the toolbar.
4. To draw a shape simply click in the model area with LMB. Make sure that `D` button in the toolbar is active. To enclose a polygon use a double-click.
5. Mouse works in 3 separate modes: draw (denoted with `D`), move (`M`) and resize (`R`). These can be switched by using the appropriate toolbar button. Draw is used to intoduce new shapes to the model, whereas move and resize may be employed to edit existing ones.
6. You can also edit shapes by using RMB popup, both in the model area and in the shapes list to the right.
7. Zoom the view in and out with `+` and `-` buttons in the toolbar. View can be reset to default using `View/Reset zoom` item from the main menu.
8. `Settings` item in the main menu allows to adjust display and models settings, such as: axis ticks interval, model size, space discretisation, alongside with survey scan parameters.
9. gprMax input files could be imported using `File/Read model file` menu item.
10. To parse created model, save result file and run gprMax simulation either click `Parse to gprMax` button in the toolbar or use `File\Parse to gprMax` item from the main menu.
11. After work is finished the conda environment may be deactivated with `conda deactivate`.

__Warning!__ Currently program does not support invoking gprMax for computations in \*nix systems.
