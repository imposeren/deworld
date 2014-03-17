# -*- coding: utf-8 -*-

# system:
import math

# PySide:
from PySide import QtGui, QtCore

# matplotlib
import matplotlib
from matplotlib.figure import Figure
from matplotlib import cm
matplotlib.rcParams['backend.qt4'] = "PySide"

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D

# deworld:
from deworld.layers import LAYER_TYPE
from deworld.cartographer import temperature_colorizer
from deworld.visualise.utils import temperature_bar_size_box


class Communicate(QtCore.QObject):

    add_power_point_start = QtCore.Signal()
    add_power_point_chosen = QtCore.Signal(tuple)
    map_cell_selected = QtCore.Signal(tuple)

    def __init__(self):
        super(Communicate, self).__init__()
        self.state = {}
        self.state['adding_power_point'] = False


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):

        self.figure = Figure(facecolor=(0, 0, 0))
        super(PlotCanvas, self).__init__(self.figure)
        self.setParent(parent)

        self.details = (0, )
        #self.details = (-0.5, 0.5)

        self.axes = self.figure.add_subplot(111, projection='3d')
        self.rerender()

    def render_surface(self, layer_name, colormap, **kwargs):
        data = self.get_data(layer_name)
        self.axes.plot_trisurf(*data, cmap=colormap, **kwargs)

    def render_bars(self, layer_name, colorizer, flat=False, bar_size=0.1):
        data = self.get_data('layer_temperature')
        temp_colors = [colorizer(t).norm_rgb for t in data[2]]
        if not flat:
            height_data = self.get_data('layer_height')
        else:
            height_data = [[], [], []]
            height_data[2] = [0 for x in data[0]]

        if callable(bar_size):
            dx = bar_size(data[2], 'x')
            dy = bar_size(data[2], 'y')
            dz = bar_size(data[2], 'z')
        else:
            dx, dy = [bar_size] * 2
            dz = data[2]
        self.axes.bar3d(
            data[0], data[1], height_data[2],
            dx, dy, dz,
            color=temp_colors, linewidth=0
        )

    def rerender(self):
        self.axes.clear()
        self.axes.set_zlim(-1, 1.5)

        # height:
        self.render_surface('layer_height', self.visualiser.cmap['height'], linewidth=0.1)

        # temperature:
        self.render_bars('layer_temperature', temperature_colorizer, bar_size=temperature_bar_size_box)

        self.draw()

    def get_data(self, layer_name):
        layer = getattr(self.world, layer_name)

        x_data = []
        y_data = []
        z_data = []
        for y, row in enumerate(layer.data):
            for x, value in enumerate(row):
                for delta in self.details:
                    x_data.append(x+delta)
                    y_data.append(y+delta)
                    z_data.append(value)
        return y_data, x_data, z_data

    @property
    def world(self):
        return self.parent().visualiser.world

    @property
    def visualiser(self):
        return self.parent().visualiser


class PlotWidget(QtGui.QWidget):
    def __init__(self, visualiser):
        super(PlotWidget, self).__init__()
        self.visualiser = visualiser

        self.setMinimumSize(QtCore.QSize(650, 500))
        self.plot_canvas = PlotCanvas(parent=self)

    def rerender(self):
        self.plot_canvas.rerender()


class MapDrawer(QtGui.QWidget):
    def __init__(self, visualiser):
        super(MapDrawer, self).__init__()
        self.visualiser = visualiser
        self.cell_size = (10, 10)
        self.do_highlight_hover = False
        self.active_cell = None

        self.setMinimumSize(*self.map_size)

        self.grid_color = QtGui.QColor(150, 150, 150)

    @property
    def world(self):
        return self.visualiser.world

    @property
    def comm(self):
        return self.visualiser.comm

    def draw_map(self, qp):
        layer = getattr(self.world, 'layer_%s' % self.visualiser.layer)
        x = 0
        y = 0
        qp.setPen(self.grid_color)
        for row in layer.data:
            for cell in row:
                color = self.visualiser.colorizer(cell, discret=False).rgb
                qp.setBrush(QtGui.QColor(*color))
                qp.drawRect(x, y, *self.cell_size)
                x += self.cell_size[0]
            y += self.cell_size[1]
            x = 0

        qp.setBrush(QtGui.QColor(0, 0, 0))
        for power_point in self.world.power_points.values():
            if power_point.layer_type == getattr(LAYER_TYPE, self.visualiser.layer.upper()):
                x, y = self.get_draw_coords(power_point.x, power_point.y, 'center')
                qp.drawEllipse(QtCore.QPointF(x, y), self.cell_size[0]/3, self.cell_size[1]/3)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_map(qp)
        if self.do_highlight_hover:
            self.highlight(qp)
        qp.end()

    def highlight(self, qp):
        if self.active_cell:
            qp.setPen(QtGui.QColor(230, 230, 0))
            qp.setBrush(QtCore.Qt.NoBrush)
            x, y = self.get_draw_coords(*self.active_cell)
            qp.drawRect(x, y, *self.cell_size)

    def get_world_coords(self, x, y):
        world_x = math.floor(x / self.cell_size[0])
        world_y = math.floor(y / self.cell_size[0])
        return int(world_x), int(world_y)

    def get_draw_coords(self, world_x, world_y, anchor='top_left'):
        x = world_x * self.cell_size[0]
        y = world_y * self.cell_size[1]
        if anchor == 'top_left':
            pass
        elif anchor == 'center':
            x += int(self.cell_size[0] / 2)
            y += int(self.cell_size[1] / 2)
        else:
            raise ValueError('Unknown anchor type')
        return x, y

    def get_active_cell(self, event):
        x, y = event.pos().toTuple()
        active_cell = self.get_world_coords(x, y)
        return active_cell

    def mouseMoveEvent(self, event):
        old_active_cell = self.active_cell
        self.active_cell = self.get_active_cell(event)
        if self.active_cell != old_active_cell:
            self.repaint()

    def mouseDoubleClickEvent(self, event):
        self.comm.map_cell_selected.emit(self.get_active_cell(event))

    @property
    def map_size(self):
        return (
            self.cell_size[0] * self.world.w + 1,
            self.cell_size[1] * self.world.h + 1
        )

    def highlight_hover(self, value=True):
        self.do_highlight_hover = value
        self.setMouseTracking(value)
        self.repaint()