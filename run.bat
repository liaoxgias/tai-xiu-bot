@echo off
REM Activate virtual env
call venv\Scripts\activate

REM Is activated
if "%VIRTUAL_ENV%"=="" (
    echo Error
    exit /b 1
)

REM Run script python
py test.py

REM Hiển thị log trước khi đóng
echo.
echo ---- LOG KẾT THÚC ----
echo Nhấn phím bất kỳ để thoát...
pause

REM Deactivate
call venv\Scripts\deactivate
