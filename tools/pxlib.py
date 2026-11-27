"""Мини-библиотека для процедурной пиксель-арт графики Frontier Military."""
import numpy as np
from PIL import Image

def clamp(v):
    return int(max(0, min(255, round(v))))

def shade(c, d):
    return (clamp(c[0] + d), clamp(c[1] + d), clamp(c[2] + d))

def mix(a, b, t):
    return tuple(clamp(a[i] * (1 - t) + b[i] * t) for i in range(3))

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4), dtype=np.uint8)

    def set(self, x, y, c, a=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y, x] = (c[0], c[1], c[2], a)

    def get(self, x, y):
        return tuple(int(v) for v in self.px[y, x])

    def rect(self, x0, y0, x1, y1, c, a=255):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c, a)

    def save(self, path):
        Image.fromarray(self.px, 'RGBA').save(path)

    def preview(self, path, scale=16, bg=(58, 58, 64)):
        im = Image.fromarray(self.px, 'RGBA')
        base = Image.new('RGBA', im.size, bg + (255,))
        base.alpha_composite(im)
        base.resize((self.w * scale, self.h * scale), Image.NEAREST).save(path)

def from_ascii(rows, palette):
    h = len(rows); w = len(rows[0])
    cv = Canvas(w, h)
    for y, row in enumerate(rows):
        assert len(row) == w, (y, len(row), w)
        for x, ch in enumerate(row):
            if ch != '.':
                cv.set(x, y, palette[ch])
    return cv
