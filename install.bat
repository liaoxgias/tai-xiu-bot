python -m venv venv
venv\Scripts\activate

pip install numpy playwright opencv-python pillow
playwright install chromium

venv\Scripts\deactivate
