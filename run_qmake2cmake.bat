@echo off
rem This script is not packaged in the qmake2cmake wheel.
rem It's only purpose is to provide a convenience wrapper for people who clone the repository.
rem Do not add any logic that goes beyond calling the python module with arguments.
python %~dp0\run_pro2cmake.py %*
