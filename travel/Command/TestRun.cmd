@echo off
chcp 65001 >nul

cd /d "D:\IT project\IT_TEAM_WORK\it_project"

call ".venv\Scripts\activate.bat"

echo Test Start...
python manage.py test travel -v

python -m pydevd manage.py test travel

echo calculate the coverage rate...
.venv\Scripts\python.exe -m coverage run --source='.' manage.py test travel
.venv\Scripts\python.exe -m coverage report -m
.venv\Scripts\python.exe -m coverage html

echo End, press any bottom for quiting...
pause >nul