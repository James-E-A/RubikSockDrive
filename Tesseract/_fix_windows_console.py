import platform
import re
import subprocess
import sys

from colorama import just_fix_windows_console

def fixit():
    if platform.system() == 'Windows':
        if platform.python_implementation() == 'PyPy':
            # This one should be applied ONLY on PyPy
            # https://github.com/pypy/pypy/issues/2999
            chcp_output = subprocess.check_output(['chcp.com'], encoding='ascii')
            cur_codepage = re.match(r'Active code page: (\d+)', chcp_output).group(1)
            cur_codepage_name = {437: 'cp437', 65001: 'utf-8', 28591: 'iso-8859-1'}[int(cur_codepage)]
            if sys.stdout.encoding != cur_codepage_name:
                sys.stdout.reconfigure(encoding=cur_codepage_name)
        # This one should be applied unconditionally
        just_fix_windows_console()
