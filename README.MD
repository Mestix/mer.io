## Necessities
- PyCharm (https://www.jetbrains.com/pycharm/download/)
- Python > 3.6 (https://www.python.org/downloads/)
- Pip (https://phoenixnap.com/kb/install-pip-windows)
- PyQt5 (https://pypi.org/project/PyQt5/)
- Pytest (https://www.guru99.com/pytest-tutorial.html)
- Pandas (https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
- PyInstaller (https://www.pyinstaller.org/downloads.html)

## Run commands
- Open command prompt in project folder (Windows) or terminal (PyCharm)

## Install packages
- ```pip install <package_name>```

## Run application from source
- Go to project folder, open command line and run ```python main.py```
- Or Open project in code editor, open terminal and run ```python main.py```
- Or Open project in PyCharm, select ```main.py``` and press play (run)

## Build application
- ```pyinstaller.exe --onedir --windowed --icon=assets/app_icon.ico main.py```  
- ```The output directory and ALL ITS CONTENTS will be REMOVED! Continue? (y/N)``` Press y
- Build can be found in ```/dist``` folder

## Run application as executable
- After building the application execute ```dist/main/main.exe``` to run application

## Run tests
- Tests can be found in ```/tests```  
- To run a test script in terminal run ```pytest <filename>```  
- To run all tests in terminal run ```pytest```
