## Necessities
- PyCharm (https://www.jetbrains.com/pycharm/download/)
- Python > 3.6 (https://www.python.org/downloads/)
- Pip (https://phoenixnap.com/kb/install-pip-windows)
- PyQt5 (https://pypi.org/project/PyQt5/)
- Pytest (https://www.guru99.com/pytest-tutorial.html)
- Pandas (https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
- cx_Freeze (https://cx-freeze.readthedocs.io/en/latest/installation.html)
- Git (https://git-scm.com/book/nl/v2/Aan-de-slag-Git-installeren)

## Clone repository
- Run ```git clone https://github.com/Mestix/mer.io.git```

## Setup Git large file storage for storing MSI file
- Download and install Git LFS extension by running ```git lfs install```
- Select files to be managed by Git LFS by running ```git lfs track "*.msi"```
- Add .gitattributes for tracked files by running ```git add .gitattributes```
- Migrate Git History by running ```git lfs migrate info --everything --include="*.zip"```

## Install all required packages
- Run ```pip install -r requirements.txt```

## Install package
- Run ```pip install <package_name>```

## Run application from source
- Go to project folder, open command line and run ```python main.py```
- Or Open project in code editor, open terminal and run ```python main.py```
- Or Open project in PyCharm, select ```main.py``` and press play (run)

## Build application
- Run ```python setup.py bdist_msi```
- Build can be found in ```/build``` 
- Installer can be found in ```/dist```

## Install application
- Execute ```mer.io_{version}_setup-amd64.msi``` from ```/dist``` to install the application
- A desktop shortcut will be created automatically

## Run tests
- Tests can be found in ```/tests```  
- To run a test script in terminal run ```pytest <filename>```  
- To run all tests in terminal run ```pytest```
