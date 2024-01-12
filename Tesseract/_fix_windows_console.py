import platform
import re
import subprocess
import sys

import colorama

def fix_console_encoding():
    # implementation note: MUST be run before the first read from stdin.
    # (stdout and sterr may be already written-to, albeit maybe corruptedly.)
    if platform.system() == 'Windows':
        colorama.just_fix_windows_console()
        if platform.python_implementation() == 'PyPy':
            if sys.pypy_version_info > (7, 3, 15):
                import warnings
                warnings.warn("Applying workaround for https://github.com/pypy/pypy/issues/2999")
            chcp_output = subprocess.check_output(['chcp.com'], encoding='ascii')
            cur_codepage = int(re.match(r'Active code page: (\d+)', chcp_output).group(1))
            cur_encoding = WINDOWS_CODEPAGES[cur_codepage]
            for f in [sys.stdin, sys.stdout, sys.stderr]:
                if f.encoding != cur_encoding:
                    f.reconfigure(encoding=cur_encoding)

WINDOWS_CODEPAGES = {
  437: 'ibm437',
  850: 'ibm850',
  1252: 'windows-1252',
  20127: 'us-ascii',
  28591: 'iso-8859-1',
  28592: 'iso-8859-2',
  28593: 'iso-8859-3',
  65000: 'utf-7',
  65001: 'utf-8'
}
