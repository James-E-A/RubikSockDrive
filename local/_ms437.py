"""https://stackoverflow.com/questions/46942721"""

import codecs
import encodings
from encodings import cp437 as _psf_cp437


def _x_cp437_search_function(encoding):
    if encodings.normalize_encoding(encoding) == 'x_cp437':
        return _Cp437CodecInfo
    return None

codecs.register(_x_cp437_search_function)


class _Cp437Codec(codecs.Codec):
    # https://github.com/python/cpython/blob/v3.12.1/Lib/encodings/cp437.py#L9
    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,_cp437_encoding_map)
    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,_cp437_decoding_map)

class _Cp437IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors,_cp437_encoding_map)[0]

class _Cp437IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors,_cp437_decoding_map)[0]

class _Cp437StreamWriter(_Cp437Codec,codecs.StreamWriter):
    pass

class _Cp437StreamReader(_Cp437Codec,codecs.StreamReader):
    pass

_Cp437CodecInfo = codecs.CodecInfo(
    # https://github.com/python/cpython/blob/v3.12.1/Lib/encodings/cp437.py#L34
    name='x-cp437',
    encode=_Cp437Codec().encode,
    decode=_Cp437Codec().decode,
    incrementalencoder=_Cp437IncrementalEncoder,
    incrementaldecoder=_Cp437IncrementalDecoder,
    streamreader=_Cp437StreamReader,
    streamwriter=_Cp437StreamWriter,
)


_cp437_encoding_map = _psf_cp437.encoding_map | {
  0x263a: 0x01,
  0x263b: 0x02,
  0x2665: 0x03,
  0x2666: 0x04,
  0x2663: 0x05,
  0x2660: 0x06,
  0x25cb: 0x09,
  0x2642: 0x0b,
  0x2640: 0x0c,
  0x266b: 0x0e,
  0x263c: 0x0f,
  0x25ba: 0x10,
  0x25c4: 0x11,
  0x2195: 0x12,
  0x203c: 0x13,
  0x00b6: 0x14,
  0x00a7: 0x15,
  0x25ac: 0x16,
  0x21a8: 0x17,
  0x2191: 0x18,
  0x2193: 0x19,
  0x2192: 0x1a,
  0x2190: 0x1b,
  0x221f: 0x1c,
  0x2194: 0x1d,
  0x25b2: 0x1e,
  0x25bc: 0x1d,
}


_cp437_decoding_map = _psf_cp437.decoding_map | {
  0x01: 0x263a,
  0x02: 0x263b,
  0x03: 0x2665,
  0x04: 0x2666,
  0x05: 0x2663,
  0x06: 0x2660,
  0x09: 0x25cb,
  0x0b: 0x2642,
  0x0c: 0x2640,
  0x0e: 0x266b,
  0x0f: 0x263c,
  0x10: 0x25ba,
  0x11: 0x25c4,
  0x12: 0x2195,
  0x13: 0x203c,
  0x14: 0x00b6,
  0x15: 0x00a7,
  0x16: 0x25ac,
  0x17: 0x21a8,
  0x18: 0x2191,
  0x19: 0x2193,
  0x1a: 0x2192,
  0x1b: 0x2190,
  0x1c: 0x221f,
  0x1d: 0x2194,
  0x1e: 0x25b2,
  0x1d: 0x25bc,
}
