from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.graphics.vertex_instructions import (Line)
from kivy.graphics.context_instructions import Color

from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.popup import Popup


class VVHelix(Widget):
    node_from, node_to = ObjectProperty(None), ObjectProperty(None)
    vvhelix_id = NumericProperty(0)

    def __init__(self, **kwargs):
        self.node_from = kwargs["from_node"]
        self.node_to = kwargs["to_node"]
        self.vvhelix_id = kwargs["vvhelix_id"]

        print(self.vvhelix_id)
        self.bind_to_nodes()
        try:
            # Note, current version is allergic against new arguments (not Kivy ones)
            # super(VVHelix, self).__init__(**kwargs)
            super().__init__()  # new way of writing the super function
        except:
            print("error is here")
        self.draw_vvhelix()

    def draw_vvhelix(self):
        # Draw the thing
        fc = self.node_from.center
        tc = self.node_to.center
        x1, y1, x2, y2 = fc[0], fc[1], tc[0], tc[1]
        points = [x1, y1, x2, y2]
        with self.canvas.before:
            Color(0, 0, 1, 1)
            Line(points=points, width=3)

    def bind_to_nodes(self):
        ln = self.node_from
        tn = self.node_to
        neighbors = ln.get_neighbors()[0]
        show_popup = False
        if neighbors[tn] == "left":
            if not ln.left_connection and not tn.right_connection:
                ln.left_connection = self
                tn.right_connection = self

                print("last - left", ln.grid_id)
                print("current - right", tn.grid_id)
                print(self)

            else:
                show_popup = True

        if neighbors[tn] == "right":
            if not ln.right_connection and not tn.left_connection:
                ln.right_connection = self
                tn.left_connection = self

                print("last - right", ln.grid_id)
                print("current - left", tn.grid_id)
                print(self)

            else:
                show_popup = True

        if neighbors[tn] == "top_right":
            if not ln.right_top_connection and not tn.left_bottom_connection:
                ln.right_top_connection = self
                tn.left_bottom_connection = self

                print("last - top_right", ln.grid_id)
                print("current - left_bottom", tn.grid_id)
                print(self)

            else:
                show_popup = True

        if neighbors[tn] == "top_left":
            if not ln.left_top_connection and not tn.right_bottom_connection:
                ln.left_top_connection = self
                tn.right_bottom_connection = self

                print("last - top_left", ln.grid_id)
                print("current - right_bottom", tn.grid_id)
                print(self)

            else:
                show_popup = True

        if neighbors[tn] == "bottom_right":
            if not ln.right_bottom_connection and not tn.left_top_connection:
                ln.right_bottom_connection = self
                tn.left_top_connection = self

                print("last - right_bottom", ln.grid_id)
                print("current - top_left", tn.grid_id)
                print(self)

            else:
                show_popup = True

        if neighbors[tn] == "bottom_left":
            if not ln.left_bottom_connection and not tn.right_top_connection:
                ln.left_bottom_connection = self
                tn.right_top_connection = self

                print("last -  left_bottom", ln.grid_id)
                print("current - right_top", tn.grid_id)
                print(self)
            else:
                show_popup = True

        if show_popup:
            txt = "Side already used up !"
            popup = Popup(
                    title="Side taken.",
                    content=Label(text=txt),
                    size_hint=(None, None),
                    size=(400, 200))
            popup.open()
            raise Exception(msg="side already usedup")
