# -*- coding: utf-8 -*-
from noise import snoise2


def get_value(x, y):
    octaves = 1
    freq = 16.0 * octaves
    return int(snoise2(x / freq, y / freq, octaves) * 127.0 + 128.0)
