:: @chcp 852>NUL
@echo off
set conda_dir=C:\ProgramData\Miniconda3
set gprmax_dir="C:\Users\ùapy precz!\Desktop\Praca magisterska\gprmax\gprMax"
call %conda_dir%\Scripts\activate.bat %conda_dir%
cd %gprmax_dir%
if "%1"=="compute" (activate gprMax & python -m gprMax %2 %3 %4 %5 & conda deactivate & pause & exit)
if "%1"=="merge" (activate gprMax & python -m tools.outputfiles_merge %2 %3 & conda deactivate & echo Merge complete & pause & exit)
if "%1"=="ascan" (activate gprMax & python -m tools.plot_Ascan %2 --outputs %3 %4 %5 %6 %7 %8 %9 & conda deactivate & exit)
if "%1"=="bscan" (activate gprMax & python -m tools.plot_Bscan %2 %3 & conda deactivate & exit)