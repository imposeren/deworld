# -*- coding: utf-8 -*-

# system:
import sys

# thirdparty:
from PySide import QtGui

# deworld:
from deworld.world import World
from deworld.configs import BaseConfig
from deworld.map_colors import HeightColorMap


class Visualiser(QtGui.QWidget):

    def __init__(self):
        super(Visualiser, self).__init__()
        self.world = World(25, 25, BaseConfig)
        self.world.do_step()
        self.cell_size = (10, 10)

        self.initUI()

    @property
    def map_size(self):
        return self.cell_size[0] * self.world.w, self.cell_size[1] * self.world.h

    def initUI(self):
        self.setGeometry(300, 300, *self.map_size)
        self.setWindowTitle('DeWorld Visualiser')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_map(qp)
        qp.end()

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


def main():

    app = QtGui.QApplication(sys.argv)
    vis = Visualiser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
