@echo off
rem batch file to build all maya plugins at once
set list= 2017 2018 2019 2020 2021

if not exist "%~dp0\build" mkdir %~dp0\build
cd %~dp0\build


del *.* /Q

for %%a in (%list%) do (
    echo %%a
    IF %%a GEQ 2020 (
        cmake -G "Visual Studio 15 2017 Win64" -DMAYA_VERSION=%%a ../
    ) ELSE (
   		cmake -G "Visual Studio 14 2015 Win64" -DMAYA_VERSION=%%a ../
    )
    cmake --build . --config Release --target Install
    pause
    del *.* /Q
)
pause