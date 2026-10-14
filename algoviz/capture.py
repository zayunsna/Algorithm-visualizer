"""PNG capture also works with minimal pygame builds without imageext."""
import struct
import zlib
from pathlib import Path
import pygame


def save_png(surface, path):
    width, height = surface.get_size()
    pixels = pygame.image.tobytes(surface, 'RGB')
    rows = b''.join(b'\0' + pixels[y*width*3:(y+1)*width*3] for y in range(height))
    def chunk(name, data):
        return struct.pack('!I', len(data)) + name + data + struct.pack('!I', zlib.crc32(name+data))
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width,height,8,2,0,0,0))
                           + chunk(b'IDAT',zlib.compress(rows)) + chunk(b'IEND',b''))
