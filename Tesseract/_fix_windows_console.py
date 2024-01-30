import io
import os
import platform
import sys
import warnings

try:
    from ctypes import windll
except ImportError:
    assert platform.system() != 'Windows'

import colorama  # pip install "colorama >= 0.4.6"


def fix_console_encoding():
    for f in [sys.stderr, sys.stdout, sys.stdin]:
        fix_tty_encoding(f)
    colorama.just_fix_windows_console()


def fix_tty_encoding(f, **k):
    cur_encoding = get_tty_encoding(f)
    if cur_encoding is None:
        # TTY doesn't *have* an encoding to fix
        return
    cur_python_encoding = f.encoding
    if cur_python_encoding == cur_encoding:
        # TTY doesn't need to be fixed
        return
    try:
        f.reconfigure(encoding=cur_encoding, **k)
    except (io.UnsupportedOperation, LookupError) as err:
        if cur_encoding.startswith('x-ebcdic'):
            try: f.reconfigure(encoding='cp037')
            except (io.UnsupportedOperation, LookupError): pass
        warnings.warn(
            RuntimeWarning(*err.args).with_traceback(err.__traceback__), stacklevel=2)


def get_tty_encoding(f=sys.stdout):
    if not f.isatty():
        # Not a TTY, so doesn't have a TTY encoding
        return None
    if platform.system() == 'Windows':
        if _check_pep528(f):
            # Python vendor special-cases Windows Console IO behind-the-scenes
            # Synthetic file doesn't have an "encoding"
            return None
        else:
            # Need to actually look it up
            cpno = _get_winconsole_codepage(f)
            return _EXTRA_MS_CODEPAGES.get(cpno, f'cp{cpno%2000:03d}')
    else:
        return _deduce_ioencoding(os.environ)


def _check_pep528(f):
    if not f.isatty():
        return False
    if platform.python_implementation() == 'CPython':
        if sys.version_info >= (3, 6):
            # https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep528
            return True
    if platform.python_implementation() == 'PyPy':
        if (
            (sys.pypy_version_info >= (8, -1))  # FIXME PENDING ISSUE GH-2999
            or (not isinstance(f.buffer.raw, io.FileIO))
        ):
            # https://github.com/pypy/pypy/issues/2999
            return True
    return False


def _get_winconsole_codepage(f):
    assert platform.system() == 'Windows'
    assert f.name in {'<stdin>', '<stdout>', '<stderr>'}
    if isinstance(f.buffer, io.BufferedWriter):
        return windll.kernel32.GetConsoleOutputCP()
    if isinstance(f.buffer, io.BufferedReader):
        return windll.kernel32.GetConsoleCP()


def _deduce_ioencoding(environ):
    if 'PYTHONIOENCODING' in environ:
        # https://docs.python.org/3/using/cmdline.html#envvar-PYTHONIOENCODING
        # https://github.com/python/cpython/blob/v3.12.1/Python/initconfig.c#L2001
        return encodings.normalize_encoding(environ['PYTHONIOENCODING'].split(':')[0])
    warnings.warn('untested codepath in _deduce_ioencoding')
    if 'LC_CTYPE' in environ:
        # https://drj11.wordpress.com/2007/05/14/python-how-is-sysstdoutencoding-chosen/#:~:text=BUT%20WHERE%20THE%20HELL%20IS%20THIS%20DOCUMENTED%3F
        # https://github.com/python/cpython/blob/v3.12.1/Python/preconfig.c#L790
        # https://github.com/python/cpython/blob/v3.12.1/Python/pylifecycle.c#L319
        return encodings.normalize_encoding(environ.get('LC_CTYPE', 'C.UTF-8').split('.')[-1])
    return sys.stdout.encoding


_EXTRA_MS_CODEPAGES = {  # https://learn.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
  708: 'iso-8859-6',
  709: 'iso-9036',
  932: 'shift_jis',
  936: 'gb2312',
  950: 'big5',
  1047: 'x-ebcdic-latin1',
  1140: 'x-ebcdic-us-ca-eu',
  1141: 'x-ebcdic-de-eu',
  1142: 'x-ebcdic-dk-no-eu',
  1143: 'x-ebcdic-fi-se-eu',
  1144: 'x-ebcdic-it-eu',
  1145: 'x-ebcdic-es-eu',
  1146: 'x-ebcdic-gb-eu',
  1147: 'x-ebcdic-fr-eu',
  1148: 'x-ebcdic-int-eu',
  1149: 'x-ebcdic-is-eu',
  1200: 'utf-16le',
  1201: 'utf-16be',
  1250: 'windows-1250',
  1251: 'windows-1251',
  1252: 'windows-1252',
  1253: 'windows-1253',
  1254: 'windows-1254',
  1255: 'windows-1255',
  1256: 'windows-1256',
  1257: 'windows-1257',
  1258: 'windows-1258',
  1361: 'johab',
  10000: 'macintosh',
  10001: 'x-mac-japanese',
  10002: 'x-mac-trad-chinese',
  10003: 'x-mac-korean',
  10004: 'mac-arabic',
  10005: 'x-mac-hebrew',
  10006: 'mac-greek',
  10007: 'mac-cyrillic',
  10008: 'x-mac-simp-chinese',
  10010: 'mac-romanian',
  10017: 'x-mac-ukrainian',
  10021: 'x-mac-thai',
  10029: 'mac-centeuro',
  10079: 'mac-iceland',
  10081: 'mac-turkish',
  10082: 'mac-croatian',
  12000: 'utf-32le',
  12001: 'utf-32be',
  20000: 'x-chinese-cns',
  20001: 'x-cp20001',
  20002: 'x-chinese-eten',
  20105: 'x-ia5',
  20106: 'x-ia5-german',
  20107: 'x-ia5-swedish',
  20108: 'x-ia5-norwegian',
  20127: 'us-ascii',
  20277: 'x-ebcdic-dk-no',
  20278: 'x-ebcdic-fi-se',
  20280: 'x-ebcdic-it',
  20284: 'x-ebcdic-es',
  20285: 'x-ebcdic-gb',
  20290: 'x-ebcdic-jp-kana',
  20297: 'x-ebcdic-fr',
  20420: 'x-ebcdic-ar1',
  20423: 'x-ebcdic-gr',
  20833: 'x-ebcdic-koreanextended',
  20838: 'x-ebcdic-thai',
  20866: 'koi8-r',
  20932: 'euc-jp',
  20936: 'x-cp20936',
  20949: 'x-cp20949',
  21866: 'koi8-u',
  28591: 'iso-8859-1',
  28592: 'iso-8859-2',
  28593: 'iso-8859-3',
  28594: 'iso-8859-4',
  28595: 'iso-8859-5',
  28596: 'iso-8859-6',
  28597: 'iso-8859-7',
  28598: 'iso-8859-8',
  28599: 'iso-8859-9',
  28603: 'iso-8859-13',
  28605: 'iso-8859-15',
  38598: 'iso-8859-8-i',
  50220: 'iso-2022-jp',
  50221: 'csiso2022jp',
  50222: 'iso-2022-jp',
  50225: 'iso-2022-kr',
  50227: 'x-cp50227',
  51932: 'euc-jp',
  51936: 'euc-cn',
  51949: 'euc-kr',
  52936: 'hz-gb-2312',
  54936: 'gb18030',
  57002: 'x-iscii-de',
  57003: 'x-iscii-be',
  57004: 'x-iscii-ta',
  57005: 'x-iscii-te',
  57006: 'x-iscii-as',
  57007: 'x-iscii-or',
  57008: 'x-iscii-ka',
  57009: 'x-iscii-ma',
  57010: 'x-iscii-gu',
  57011: 'x-iscii-pa',
  65000: 'utf-7',
  65001: 'utf-8'}

try:
    from . import _ms437
except ImportError:
    pass
else:
    _EXTRA_MS_CODEPAGES[437] = 'x-cp437'


if __name__ == '__main__':
    # Use with python -i, for example
    fix_console_encoding()
