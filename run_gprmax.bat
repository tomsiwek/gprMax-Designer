:: @chcp 852>NUL
@echo off
set conda_dir=C:\ProgramData\Miniconda3
set gprmax_dir="C:\Users\ùapy precz!\Desktop\Praca magisterska\gprmax\gprMax-v.3.1.4"
call %conda_dir%\Scripts\activate.bat %conda_dir%
cd %gprmax_dir%
activate gprMax & python -m gprMax %1 %2 %3 %4 & conda deactivate & pause & exit