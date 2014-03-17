# -*- coding: utf-8 -*-


def temperature_bar_size_box(data, axis):
    """
    Assumes that data values are from -1 to 1

    """
    if axis == 'z':
        multiplier = 0.2 / 4
    else:
        multiplier = 1.0 / 4
    return [multiplier * (v+1) for v in data]
