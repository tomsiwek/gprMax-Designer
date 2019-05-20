@echo off
set conda_dir="C:\path_to_conda"
set gprmax_dir="C:\path_to_gprmax"
call %conda_dir%\Scripts\activate.bat %conda_dir%
cd %gprmax_dir%
activate gprMax & python -m gprMax %1 %2 %3 %4 & conda deactivate & pause & exit
