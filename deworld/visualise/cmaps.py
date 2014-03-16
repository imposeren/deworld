# -*- coding: utf-8 -*-
import matplotlib
from matplotlib.colors import colorConverter

# generate the transparent colors
terrain_bot = colorConverter.to_rgba('#71abd8', alpha=0.7)
terrain_mid = colorConverter.to_rgba('#acd0a5', alpha=0.7)
terrain_high = colorConverter.to_rgba('#c3a76b', alpha=0.7)
terrain_top = colorConverter.to_rgba('#f5f4f2', alpha=0.7)

# make the colormaps
red_cyan_transp = matplotlib.colors.LinearSegmentedColormap.from_list('my_cmap2', [terrain_bot, terrain_mid, terrain_high, terrain_top], 256)
