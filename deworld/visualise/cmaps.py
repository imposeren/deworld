# -*- coding: utf-8 -*-
import matplotlib
from matplotlib.colors import colorConverter

# generate the transparent colors
cyan_transp = colorConverter.to_rgba('cyan', alpha=0.4)
red_transp = colorConverter.to_rgba('red', alpha=0.4)

# make the colormaps
red_cyan_transp = matplotlib.colors.LinearSegmentedColormap.from_list('my_cmap2', [cyan_transp, red_transp], 256)
