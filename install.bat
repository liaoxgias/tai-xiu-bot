@echo off
REM Tạo môi trường ảo Python
python -m venv venv

REM Kiểm tra xem venv đã được tạo thành công chưa
if not exist venv (
    echo Lỗi: Không thể tạo môi trường ảo!
    exit /b 1
)

REM Kích hoạt môi trường ảo
call venv\Scripts\activate

REM Kiểm tra xem môi trường ảo đã được kích hoạt chưa
if "%VIRTUAL_ENV%"=="" (
    echo Lỗi: Không thể kích hoạt môi trường ảo!
    exit /b 1
)

REM Cài đặt các thư viện cần thiết
pip install --upgrade pip
pip install numpy playwright opencv-python pillow

REM Cài đặt trình duyệt cho Playwright
playwright install chromium

REM Hủy kích hoạt môi trường ảo
call venv\Scripts\deactivate

echo Hoàn thành!
pause
