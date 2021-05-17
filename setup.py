from cx_Freeze import setup, Executable

from src.environment import environment
import sys


build_options = {
    'packages': [],
    'excludes': [],
    'include_files': ['src/assets']
}

msi_options = {
    'target_name': 'mer.io_{0}_setup'.format(environment['version']),
    'install_icon': 'src/assets/icons/app_icon.ico',
    'upgrade_code': '{2967c71a-9bf5-48be-b9db-b2c5a6c9fab6}'
}

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('src/main.py',
               base=base,
               shortcut_name="Mer.io",
               shortcut_dir="DesktopFolder",
               icon='src/assets/icons/app_icon.ico',
               target_name='mer.io')
]

setup(name='mer.io',
      version=environment['version'],
      description='mer extraction tool',
      options={
          'build_exe': build_options,
          'bdist_msi': msi_options},
      executables=executables,
)
