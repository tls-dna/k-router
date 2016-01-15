from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty, BoundedNumericProperty, ListProperty
from .node import Node

from math import sqrt


class HexCanvas(FloatLayout):
    last_node = ObjectProperty(None, allownone=True)
    grid = ObjectProperty([])
    row_count = BoundedNumericProperty(11, min=0, max=11)
    column_count = BoundedNumericProperty(22, min=0, max=22)

    vvhelix_id = NumericProperty(0)

    scaffold_path = ListProperty([])

    """docstring for NanoCanvas"""

    def __init__(self, **kwargs):
        #super(HexCanvas, self).__init__(**kwargs)
        super().__init__(**kwargs)
        self.__construct()

    def __construct(self):
        x_start, y_start = 30, 30
        a = 60
        x_offset = a / 2
        y_offset = a * sqrt(3) / 2
        y = y_start
        for j in range(self.row_count):
            row = []
            if j % 2 != 0:
                offset = x_offset
            else:
                offset = 0
            x = x_start + offset
            for i in range(self.column_count):
                node = Node(pos=(x, y), grid_id=(j, i))
                row.append(node)
                self.add_widget(node)
                x += a
            y += y_offset
            self.grid.append(row)

    def clean(self):
        # TODO remove vhelixes and other stuff !!!
        self.last_node = None
        # for row in self.grid:
        #    for node in row:
        #        del node
        self.grid = []

        self.vvhelix_id = 0
        self.scaffold_path = []

        self.__construct()
