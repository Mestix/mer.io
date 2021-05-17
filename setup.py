from cx_Freeze import setup, Executable

from src.environment import environment
import sys

base = 'Win32GUI' if sys.platform == 'win32' else None

shortcut_table = [
    ("DesktopShortcut",                         # Shortcut
     "DesktopFolder",                           # Directory_
     "Mer.io",                                  # Name
     "TARGETDIR",                               # Component_
     "[TARGETDIR]mer.io.exe",                   # Target
     None,                                      # Arguments
     None,                                      # Description
     None,                                      # Hotkey
     '',                                        # Icon
     None,                                      # IconIndex
     None,                                      # ShowCmd
     'TARGETDIR'                                # WkDir
     )
    ]

build_options = {
    'packages': [],
    'excludes': [],
    'include_files': ['src/assets'],
}

msi_options = {
    'target_name': 'mer.io_{0}_setup'.format(environment['version']),
    'upgrade_code': '{2967c71a-9bf5-48be-b9db-b2c5a6c9fab6}',
    'data': {'Shortcut': shortcut_table}
}

executables = [
    Executable('src/main.py',
               base=base,
               target_name='mer.io',
               icon='src/assets/icons/app_icon.ico')
]

setup(name='mer.io',
      version=environment['version'],
      description='mer extraction tool',
      options={
          'build_exe': build_options,
          'bdist_msi': msi_options
      },
      executables=executables,
      )
