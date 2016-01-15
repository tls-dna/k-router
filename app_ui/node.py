import sys
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.uix.popup import Popup
from .vvhelix import VVHelix

from kivy.graphics.vertex_instructions import (Line, Ellipse)
from kivy.graphics.context_instructions import Color

from math import sin, cos, pi


class Node(Label):
    radius = NumericProperty(12)
    grid_id = ListProperty((0, 0))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.draw_roze()

    # Connections for the graph
    left_connection = ObjectProperty(None)
    right_connection = ObjectProperty(None)
    left_top_connection = ObjectProperty(None)
    right_top_connection = ObjectProperty(None)
    left_bottom_connection = ObjectProperty(None)
    right_bottom_connection = ObjectProperty(None)

    # who was added when (to reconstruct scaffold path at node level)
    connections_order = []

    def draw_roze(self):
        # first draw base
        for z in range(6):
            angle = 2 * pi / 6 * z
            x1 = round(self.center[0] + self.radius * cos(angle))
            y1 = round(self.center[1] + self.radius * sin(angle))
            x2 = round(self.center[0] + (self.radius + 10) * cos(angle))
            y2 = round(self.center[1] + (self.radius + 10) * sin(angle))
            points = [x1, y1, x2, y2]
            with self.canvas.before:
                Color(0, 1, 0, 1)
                Line(points=points, width=1)

    # noinspection PyBroadException
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            ln = self.parent.last_node
            try:
                if ln:
                    # fill up the connection graph With helices
                    neighbors = ln.get_neighbors()[0]
                    # for ->
                    if self in neighbors:
                        vvh = VVHelix(from_node=ln, to_node=self, vvhelix_id=self.parent.vvhelix_id)

                        self.parent.vvhelix_id += 2
                        self.parent.add_widget(vvh)
                        # to generate the design - we are interested in the order of the vvhelixes added
                        self.parent.scaffold_path.append(vvh)
                    else:
                        txt = " ".join([str(self.grid_id), "not a neighbor of", str(ln.grid_id)])
                        popup = Popup(
                            title="Not a neighbor.",
                            content=Label(text=txt),
                            size_hint=(None, None),
                            size=(400, 200))
                        popup.open()
                        return True
                self.parent.last_node = self
                with self.canvas.before:
                    Color(1, 1, 1, 1)
                    Ellipse(pos=(self.center[0] - 6, self.center[1] - 6), size=(12, 12))
                return True
            except:
                print(sys.exc_info()[0])
                pass

    def get_neighbors(self):
        y, x = self.grid_id
        object_value = {}
        value_object = {}
        # left
        x_, y_ = x - 1, y
        if x_ >= 0:
            object_value[self.parent.grid[y_][x_]] = "left"
            value_object["left"] = self.parent.grid[y_][x_]
        # right
        x_, y_ = x + 1, y
        if x_ < self.parent.column_count:
            object_value[self.parent.grid[y_][x_]] = "right"
            value_object["right"] = self.parent.grid[y_][x_]

        # to correct for the grid offset
        if y % 2 != 0:
            offset = 1
        else:
            offset = 0

        x += offset

        # left top
        x_, y_ = x - 1, y + 1
        if y_ < self.parent.row_count and x_ >= 0:
            object_value[self.parent.grid[y_][x_]] = "top_left"
            value_object["top_left"] = self.parent.grid[y_][x_]

        # right top
        x_, y_ = x, y + 1
        if y_ < self.parent.row_count and x_ < self.parent.column_count:
            object_value[self.parent.grid[y_][x_]] = "top_right"
            value_object["top_right"] = self.parent.grid[y_][x_]

        # bottom left
        x_, y_ = x - 1, y - 1
        if y_ >= 0 and x_ >= 0:
            object_value[self.parent.grid[y_][x_]] = "bottom_left"
            value_object["bottom_left"] = self.parent.grid[y_][x_]

        # bottom right
        x_, y_ = x, y - 1
        if y_ >= 0 and x_ < self.parent.column_count:
            object_value[self.parent.grid[y_][x_]] = "bottom_right"
            value_object["bottom_right"] = self.parent.grid[y_][x_]

        return object_value, value_object

    def helix_to_slot(self, helix):
        if helix == self.right_connection:
            return 0
        if helix == self.right_top_connection:
            return 1
        if helix == self.left_top_connection:
            return 2
        if helix == self.left_connection:
            return 3
        if helix == self.left_bottom_connection:
            return 4
        if helix == self.right_bottom_connection:
            return 5

    def number_to_helix(self, number):
        if number < 0:
            return self.right_bottom_connection
        if number == 0:
            return self.right_connection
        if number == 1:
            return self.right_top_connection
        if number == 2:
            return self.left_top_connection
        if number == 3:
            return self.left_connection
        if number == 4:
            return self.left_bottom_connection
        if number == 5:
            return self.right_bottom_connection
        if number > 5:
            return self.right_connection
        return None
