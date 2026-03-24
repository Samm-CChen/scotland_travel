cd D:\IT project\IT_TEAM_WORK\it_project
Import-Module .venv
.venv\Scripts\activate

python --version
pip show django

pip uninstall django -y
pip install django==3.2.25

pip install setuptools==3.2.25
pip install distutils

pip list | grep django