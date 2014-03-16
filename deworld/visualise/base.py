# -*- coding: utf-8 -*-
# system:
import sys

# PySide:
from PySide import QtGui

# deworld:
from deworld import power_points
from deworld import normalizers
from deworld.world import World
from deworld.configs import BaseConfig
from deworld.cartographer import temperature_colorizer
from deworld.layers import LAYER_TYPE
from deworld.map_colors import HeightColorMap
from deworld.visualise.widgets import Communicate, MapDrawer, PlotWidget
from deworld.visualise.cmaps import red_cyan_transp


class Visualiser(QtGui.QWidget):

    def __init__(self, world=None):
        super(Visualiser, self).__init__()
        if world is None:
            self.world = World(25, 25, BaseConfig)
            self.randomize_world()
        else:
            self.world = world

        self.layer = 'height'
        self.colorizer = HeightColorMap.get_color
        self.cmap = red_cyan_transp
        self.power_value = (0, 0.75)
        self.default_power = (0, 0)
        self.normalizer = normalizers.linear_2

        self.initUI()
        self.subscribe_signals()

    def randomize_world(self):
        from deworld.visualise.random_texture import get_value
        for x in range(self.world.w):
            for y in range(self.world.h):
                value = get_value(x, y) * 1.0 / 256
                self.world.layer_height.data[y][x] = value

    def initUI(self):
        self.comm = Communicate()
        self.map_widget = MapDrawer(self)
        self.plot_widget = PlotWidget(self)
        self.step_button = QtGui.QPushButton(u'Do step')
        self.add_power_button = QtGui.QPushButton(u'Add power point')

        self.layers_combo = QtGui.QComboBox(self)
        self.layers_combo.addItem('Height')
        self.layers_combo.addItem('Temperature')

        grid = QtGui.QGridLayout()

        grid.addWidget(self.map_widget, 1, 0, 3, 1)
        grid.addWidget(self.plot_widget, 4, 0)
        grid.addWidget(self.step_button, 1, 1)
        grid.addWidget(self.add_power_button, 2, 1)
        grid.addWidget(self.layers_combo, 3, 1)
        self.buttons = (self.step_button, self.add_power_button)
        self.other_elems = (self.layers_combo, )

        self.setLayout(grid)
        w, h = self.map_widget.map_size
        self.setWindowTitle(u'DeWorld Visualiser')
        self.show()

    def subscribe_signals(self):
        self.step_button.clicked.connect(self.do_step)
        self.add_power_button.clicked.connect(self.comm.add_power_point_start.emit)

        self.comm.add_power_point_start.connect(self.add_power_clicked)

        self.comm.map_cell_selected.connect(self.cell_selected)

        self.comm.add_power_point_chosen.connect(self.add_power_point_chosen)

        self.layers_combo.activated[str].connect(self.layer_activated)

    # reactions to signals:
    def redraw_all(self):
        self.map_widget.repaint()
        self.plot_widget.rerender()

    def do_step(self):
        for i in range(2):
            self.world.do_step()
        self.redraw_all()

    def disable_enable_buttons(self, value):
        for button in self.buttons:
            button.setEnabled(value)

    def disable_enable_other(self, value):
        for item in self.other_elems:
            item.setEnabled(value)

    def disable_enable_all(self, value):
        self.disable_enable_buttons(value)
        self.disable_enable_other(value)

    def add_power_clicked(self):
        self.disable_enable_all(False)
        self.map_widget.highlight_hover()
        self.comm.state['adding_power_point'] = True

    def cell_selected(self, cell):
        if self.comm.state['adding_power_point']:
            self.comm.add_power_point_chosen.emit(cell)

    def add_power_point_chosen(self, cell):
        point_name = 'circular_point_%s_%s_%s' % (self.layer.lower(), cell[0], cell[1])
        self.world.add_power_point(
            power_points.CircleAreaPoint(
                layer_type=getattr(LAYER_TYPE, self.layer.upper()),
                name=point_name,
                x=cell[0],
                y=cell[1],
                power=(lambda w, x, y: self.power_value),
                default_power=self.default_power,
                radius=4,
                normalizer=self.normalizer
            )
        )

        self.comm.state['adding_power_point'] = False
        self.map_widget.highlight_hover(False)
        self.disable_enable_all(True)

    def layer_activated(self, text):
        self.layer = text.lower()
        if self.layer == 'height':
            self.colorizer = HeightColorMap.get_color
            self.normalizer = normalizers.linear_2
            self.power_value = (0, 0.75)
            self.default_power = (0, 0)
        elif self.layer == 'temperature':
            self.colorizer = temperature_colorizer
            self.normalizer = normalizers.linear
            self.power_value = 0.5
            self.default_power = 0
        self.redraw_all()


def main():
    app = QtGui.QApplication(sys.argv)
    vis = Visualiser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
