from .codec_v2 import *
from .cube import Cube
from .ranking import _A50
from .util import callbackify

try:
  from colorama import just_fix_windows_console
except ImportError:
  def just_fix_windows_console(): pass

from pathlib import Path
import re
import sys
import textwrap

# TODO tkinter dialogue

if __name__ == '__main__':
  just_fix_windows_console()

  mode = input("What do you want to do?\nF: Send a file\n50: Send a simple text message\nEnter: receive a message\n> ").upper()

  if mode in {"F", "50"}:
    if mode == "F":
      cs = bytes_to_cubes(Path(input("Filename:\n> ")).read_bytes())

    elif mode == "50":
      print("Type your message now. End with a blank line.")
      message = '\ue01d$'.join(iter(lambda: input('> '), ''))
      message = message.upper()
      message = re.sub(rf'[^{re.escape(_A50)}]', lambda m: f"\ue01dW{m.group(0).encode('utf-16le', errors='surrogateescape').hex().upper()}", message)
      cs = str50_to_cubes(message)

    print("\n".join(repr(cube) for cube in cs))

  elif mode == "":
    print("Enter the solverstrings for the cubes you've received, one per line, in any order.")
    print("NOTE: for now, you must enter them white-up, green-front.")
    print("Example: wwwwwwwwwgggrrrbbbooogggrrrbbbooogggrrrbbboooyyyyyyyyy")
    cs = list(map(Cube, iter(lambda: input('> '), '')))

    mode = input("Were you expecting a File (F), or a simple text message (50)?\n> ").upper()
    if mode == "F":
      Path(input("Filename (WILL BE OVERWRITTEN):\n> ")).write_bytes(cubes_to_bytes(cs))

    elif mode == "50":
      message = cubes_to_str50(cs)
      message = re.sub(r'\ue01dW([0-9A-F]{4})', lambda m: bytes.fromhex(m.group(1)).decode('utf-16le', errors='surrogateescape'), message)
      print('\n'.join([
        "-----BEGIN MESSAGE-----",
        *(line for paragraph in message.split('\ue01d$')for line in textwrap.wrap(paragraph)),
        "-----END MESSAGE-----"
      ]))

    else:
      raise ValueError

  else:
    raise ValueError
