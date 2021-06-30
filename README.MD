# Setting up the project
## Necessities
- PyCharm (https://www.jetbrains.com/pycharm/download/)
- Python > 3.6 (https://www.python.org/downloads/)
- Pip (https://phoenixnap.com/kb/install-pip-windows)
- Git (https://git-scm.com/book/nl/v2/Aan-de-slag-Git-installeren)

## Clone repository
- Run ```git clone https://github.com/Mestix/mer.io.git```

## Create virtual environment
- Locate project folder, right click on folder and select open project as PyCharm project
- When opening the project folder with Pycharm, Pycharm will ask you to create a virtual environment for you (use python as interpreter) this will take a while
- If not, create a virtual environment by running ```virtualenv env --no-site-packages```
- Activate the environment by running ```source env/bin/activate```
- Install all packages by running ```pip install -r requirements.txt```

## Run application from source
- Locate project folder, right click on folder and select open project as PyCharm project
- In Pycharm explorer (left) right click on main.py and press run
- Or from project folder open command prompt run ```python src/main.py```
- Or Open project in code editor, open terminal and run ```python src/main.py```
-------------
# Maintaining the application
## Setup Git large file storage for storing MSI file
- Download and install Git LFS extension by running ```git lfs install```
- Select files to be managed by Git LFS by running ```git lfs track "*.msi"```
- Add .gitattributes for tracked files by running ```git add .gitattributes```
- Migrate Git History by running ```git lfs migrate info --everything --include="*.zip"```

## Using Git
- Use Github Desktop or Terminal (below commands when using Terminal)
- Pull the main branch run ```git pull```
- Create and go into new branch run ```git checkout -b <branchname>```
- Commit changes run ```git commit -a -M "<commit message>"``` 
- Push changes into branch ```git push``` **WARNING! never push in main branch!**
- Create a pull request at Github.com to merge changes with main branch
- When merged with main branch run ```git checkout main``` & ```git pull```
- Your changes should now be visible in the main branch

## Create or update requirements file
- Run ```pip freeze > requirements.txt```

## Install single package
- Run ```pip install <package_name>```
-------------
# Building and installing the application
## Necessities
- cx_Freeze (https://cx-freeze.readthedocs.io/en/latest/installation.html)

## Build application
- Run ```python setup.py bdist_msi```
- Build can be found in ```/build``` (not tracked by Git)
- Installer can be found in ```/dist``` (tracked by Git)
- Build settings can be found in ```setup.py```

## Install application
- Install the application by executing ```mer.io_{version}_setup-amd64.msi``` from ```/dist```
- A desktop shortcut will be created automatically

-------------
# Testing the application 
## Run tests
- Tests can be found in ```/tests```  
- Run a single test by running ```pytest <filename>```  
- Run all tests by running ```pytest```
