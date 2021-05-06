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
- Run command

## Install packages
- Run ```pip install <package_name>```

## Run application from source
- Go to project folder, open command line and run ```python main.py```
- Or Open project in code editor, open terminal and run ```python main.py```
- Or Open project in PyCharm, select ```main.py``` and press play (run)

## Build application
- Run ```python src/pyinstaller.py```
- ```pyinstaller -F --add-data venv/Lib/site-packages/qt_material;qt_material --add-data src/assets;assets src/main.py --name mer.io_v0.3.6 --icon=src/assets/app_icon.ico --noconfirm --onedir --windowed```
- Build can be found in ```/dist``` folder

## Run application as executable
- After building the application execute ```dist/mer.io_version/mer.io.exe``` to run application

## Run tests
- Tests can be found in ```/tests```  
- To run a test script in terminal run ```pytest <filename>```  
- To run all tests in terminal run ```pytest```
