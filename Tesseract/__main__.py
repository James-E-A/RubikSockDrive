from .codec_v2 import *
from .cube import Cube

from pathlib import Path
import sys

# TODO tkinter dialogue

def encode():
  arg1 = sys.argv[1] if len(sys.argv) > 1 else None
  if arg1 is None:
    x = input('Do you want to send a file, or a simple text message?\nType "50" and press Enter for simple text; or type "f" and press Enter for a file.\n> ')
    if x == '50':
      m = input('type your message\n(Only alphanumerics, spaces, and "$" to separate sentences.)\n> ')
      cs = str50_to_cubes(m)
    elif x == 'f':
      p = Path(input('specify the file path.\n> '))
      bytes_to_cubes(p.read_bytes())
    else:
      raise ValueError()
  else:
    p = Path(arg1)
    print(f'Sending file from {p}...')
    if p.suffix in {'.txt', '.TXT'}:
      cs = str50_to_cubes(p.read_text())
    else:
      cs = bytes_to_cubes(p.read_bytes())
  print('Here are the cubes containing your outbound message:')
  print('\n'.join(repr(c) for c in cs))


def decode():
  print('Enter, ONE PER LINE, the solverstrings for the cubes you recieved.\n(NOTE for now you MUST use white-up, green-front.)')
  print('Press Enter without any result once you\'ve entered all the cubes.')
  cs = []
  x = input('> ')
  while x:
    cs.append(Cube(x))
    x = input('> ')
  x = input('Were you expecting a FILE, or a SIMPLE TEXT message?\nType "50" and press Enter for simple text; or type "f" and press Enter for a file.\n> ')
  if x == '50':
    m = cubes_to_str50(cs).replace('$', '; ')
    print(f'Your message is:\n\n{m}\n')
  elif x == 'f':
    data = cubes_to_bytes(cs)
    x = input('Enter the path to save the file to\n(WARNING: will be overridden if it exists!)\n> ')
    p = Path(x)
    p.write_bytes(data)
  else:
    raise ValueError()


if __name__ == '__main__':
  if input('Do you want to send a message, or recieve one?\nPress ENTER to recieve a message, or type ANYTHING AT ALL then press Enter to send one.\n> '):
    encode()
  else:
    decode()
