# -*- coding: utf-8 -*-

# system:
import sys

# thirdparty:
from PySide import QtGui, QtCore

# deworld:
from deworld.map_colors import HeightColorMap


class Visualiser(QtGui.QWidget):

    def __init__(self, world):
        super(Visualiser, self).__init__()
        self.world = world

        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('DeWorld Visualiser')
        self.show()

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        size = self.size()
        cell_size = (
            size.width() / self.world.w,
            size.height() / self.world.h,
        )
        layer = world.layer_height
        x = 0
        y = 0
        for row in layer.data:
            for cell in row:
                color = HeightColorMap.get_color(cell, discret=False).rgb
                qp.setPen(QtGui.QColor(*color))
                qp.drawRect(x, y, cell_size[0], cell_size[1])
                x += cell_size[0]
            y += cell_size[1]


def main():

    app = QtGui.QApplication(sys.argv)
    vis = Visualiser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from deworld.generate import world
    main(world)
