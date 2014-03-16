# -*- coding: utf-8 -*-

# system:
import sys
import random

# thirdparty:
from PySide import QtGui

# deworld:
from deworld.world import World
from deworld.configs import BaseConfig
from deworld.map_colors import HeightColorMap


class MapDrawer(QtGui.QWidget):
    def __init__(self, world):
        super(MapDrawer, self).__init__()
        self.world = world
        self.cell_size = (10, 10)

        w, h =self.map_size
        self.setMinimumSize(w+1, h+1)

    def draw_map(self, qp):
        layer = self.world.layer_height
        x = 0
        y = 0
        qp.setPen(QtGui.QColor(150, 150, 150))
        for row in layer.data:
            for cell in row:
                color = HeightColorMap.get_color(cell, discret=False).rgb
                qp.setBrush(QtGui.QColor(*color))
                qp.drawRect(x, y, self.cell_size[0], self.cell_size[1])
                x += self.cell_size[0]
            y += self.cell_size[1]
            x = 0

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_map(qp)
        qp.end()

    @property
    def map_size(self):
        return self.cell_size[0] * self.world.w, self.cell_size[1] * self.world.h


class Visualiser(QtGui.QWidget):

    def __init__(self, world=None):
        super(Visualiser, self).__init__()
        if world is None:
            self.world = World(25, 25, BaseConfig)
            self.randomize_world()
        else:
            self.world = world

        self.initUI()

    def randomize_world(self):
        for x in range(self.world.w):
            for y in range(self.world.h):
                self.world.layer_height.data[y][x] = random.random()

    def initUI(self):
        self.map_widget = MapDrawer(self.world)

        grid = QtGui.QGridLayout()

        grid.addWidget(self.map_widget, 1, 0)
        grid.addWidget(QtGui.QLabel('Test'), 1, 1)

        self.setLayout(grid)
        w, h = self.map_widget.map_size
        #self.setGeometry(300, 300, w+200, h)
        self.setWindowTitle('DeWorld Visualiser')
        self.show()



def main():

    app = QtGui.QApplication(sys.argv)
    vis = Visualiser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
