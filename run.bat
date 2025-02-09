@echo off
REM Activate virtual env
call venv\Scripts\activate

REM Is activated
if "%VIRTUAL_ENV%"=="" (
    echo Error
    pause
    exit /b 1
)

REM Run script python
py test.py

REM Hiển thị log trước khi đóng

REM Deactivate
call venv\Scripts\deactivate
