import PyInstaller.__main__

from environment import environment

# Does not work, to be fixed

PyInstaller.__main__.run([
    '-F',
    '--data="venv/Lib/site-packages/qt_material;qt_material"',
    '--data="src/assets;assets"',
    'src/main.py',
    '--name mer.io_v{0}'.format(environment['version']),
    '--icon=src/assets/app_icon.ico',
    '--noconfirm',
    '--onedir',
    '--windowed'
])
