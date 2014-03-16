# -*- coding: utf-8 -*-

# system:
import sys
import random
import math
import pdb

# thirdparty:
from PySide import QtGui, QtCore

# deworld:
from deworld.world import World
from deworld.configs import BaseConfig
from deworld.map_colors import HeightColorMap
from deworld import power_points
from deworld import normalizers
from deworld.layers import LAYER_TYPE


class Communicate(QtCore.QObject):

    add_power_point_start = QtCore.Signal()
    add_power_point_chosen = QtCore.Signal(tuple)
    map_cell_selected = QtCore.Signal(tuple)

    def __init__(self):
        super(Communicate, self).__init__()
        self.state = {}
        self.state['adding_power_point'] = False


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
        layer = self.world.layer_height
        x = 0
        y = 0
        qp.setPen(self.grid_color)
        for row in layer.data:
            for cell in row:
                color = HeightColorMap.get_color(cell, discret=False).rgb
                qp.setBrush(QtGui.QColor(*color))
                qp.drawRect(x, y, *self.cell_size)
                x += self.cell_size[0]
            y += self.cell_size[1]
            x = 0

        qp.setBrush(QtGui.QColor(0, 0, 0))
        for power_point in self.world.power_points.values():
            if power_point.layer_type == LAYER_TYPE.HEIGHT:
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


class Visualiser(QtGui.QWidget):

    def __init__(self, world=None):
        super(Visualiser, self).__init__()
        if world is None:
            self.world = World(25, 25, BaseConfig)
            self.randomize_world()
        else:
            self.world = world

        self.initUI()
        self.subscribe_signals()

    def randomize_world(self):
        for x in range(self.world.w):
            for y in range(self.world.h):
                self.world.layer_height.data[y][x] = random.random()

    def initUI(self):
        self.comm = Communicate()
        self.map_widget = MapDrawer(self)
        self.step_button = QtGui.QPushButton(u'Do step')
        self.add_power_button = QtGui.QPushButton(u'Add power point')
        self.pdb_button = QtGui.QPushButton(u'PDB')

        grid = QtGui.QGridLayout()

        grid.addWidget(self.map_widget, 1, 0, 3, 1)
        grid.addWidget(self.step_button, 1, 1)
        grid.addWidget(self.add_power_button, 2, 1)
        grid.addWidget(self.pdb_button, 3, 1)
        self.buttons = (self.step_button, self.add_power_button)

        self.setLayout(grid)
        w, h = self.map_widget.map_size
        self.setWindowTitle(u'DeWorld Visualiser')
        self.show()

    def subscribe_signals(self):
        self.step_button.clicked.connect(self.do_step)
        self.add_power_button.clicked.connect(self.comm.add_power_point_start.emit)
        self.pdb_button.clicked.connect(pdb.set_trace)

        self.comm.add_power_point_start.connect(self.add_power_clicked)

        self.comm.map_cell_selected.connect(self.cell_selected)

        self.comm.add_power_point_chosen.connect(self.add_power_point_chosen)

    # reactions to signals:
    def do_step(self):
        for i in range(5):
            self.world.do_step()
        self.map_widget.repaint()

    def disable_enable_buttons(self, value):
        for button in self.buttons:
            button.setEnabled(value)

    def add_power_clicked(self):
        self.disable_enable_buttons(False)
        self.map_widget.highlight_hover()
        self.comm.state['adding_power_point'] = True

    def cell_selected(self, cell):
        if self.comm.state['adding_power_point']:
            self.comm.add_power_point_chosen.emit(cell)

    def add_power_point_chosen(self, cell):
        self.world.add_power_point(
            power_points.CircleAreaPoint(
                layer_type=LAYER_TYPE.HEIGHT,
                name='circular_point_%s_%s' % cell,
                x=cell[0],
                y=cell[1],
                power=(lambda w, x, y: (0.75, 0)),
                default_power=(0, 0),
                radius=4,
                normalizer=normalizers.linear_2
            )
        )

        self.comm.state['adding_power_point'] = False
        self.map_widget.highlight_hover(False)
        self.disable_enable_buttons(True)


def main():
    app = QtGui.QApplication(sys.argv)
    vis = Visualiser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
