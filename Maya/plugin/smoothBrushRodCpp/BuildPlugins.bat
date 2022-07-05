@echo off
rem batch file to build all maya plugins at once
set list= 2017 2018 2019 2020 2022 2023

if not exist "%~dp0\build" mkdir %~dp0\build
cd %~dp0\build


del *.* /Q

for %%a in (%list%) do (
    cmake -G "Visual Studio 16 2019" -DMAYA_VERSION=%%a ../
    cmake --build . --config Release --target Install
    del *.* /Q
)
pause