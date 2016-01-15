from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
# file Choice
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import os
from util.tools import (generate_even_helix_position_sq, vhelix,
                        interconnect_helices, interconnect_staples,
                        break_staple)
from app_ui.vvhelix import VVHelix

# for the kv declaration
# from app_ui.hexcanvas import HexCanvas
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import (Ellipse)

from kivy.core.window import Window

Window.size = (1352, 652)

Builder.load_string('''

<Node>:
    size_hint: None, None
    size: self.radius * 2.5, self.radius * 2.5

<MWindow>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: 50
        Button:
            id: btn_generate_design
            size_hint_y: None
            height: 50
            text: "Save to caDNAno"
            on_press: root.show_generate()
        Button:
            id: save_design
            size_hint_y: None
            height: 50
            text: "Save design"
            on_press: root.show_save()
        Button:
            id: load_design
            size_hint_y: None
            height: 50
            text: "Load design"
            on_press: root.show_load()

    HexCanvas:
        id: hex_grid

<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)

<SaveDialog>:
    text_input: text_input
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            on_selection: text_input.text = self.selection and self.selection[0] or ''

        TextInput:
            id: text_input
            size_hint_y: None
            height: 30
            multiline: False

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Save"
                on_release: root.save(filechooser.path, text_input.text)
''')


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


def get_used_nodes(scaffold_path):
    nodes = [vvh.node_from for vvh in scaffold_path]
    nodes.extend([vvh.node_to
                  for vvh in scaffold_path])
    return set(nodes)


def find_boundaries(connections):
    verteces = [item for sublist in connections for item in sublist]
    up, down = [0, 0], [199, 0]
    up_right, down_right = [0, 0], [199, 0]

    for v in verteces:
        if v[0] > up[0]:
            up = v
        if v[0] == up[0] and v[1] < up[1]:
            up = v

        if v[0] < down[0]:
            down = v
        if v[0] == down[0] and v[1] < down[1]:
            down = v

        if v[0] > up_right[0]:
            up_right = v
        if v[0] == up_right[0] and v[1] > up_right[1]:
            up_right = v

        if v[0] < down_right[0]:
            down_right = v
        if v[0] == down_right[0] and v[1] > down_right[1]:
            down_right = v

    return up, down, up_right, down_right


class MWindow(BoxLayout):
    def show_generate(self):
        content = SaveDialog(save=self.generate_design, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save caDNAno design", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def generate_design(self, fpath, filename):
        print("_" * 80)
        print("trying to generate_design")
        design = []
        hex_grid = self.ids.hex_grid
        scaffold_path = hex_grid.scaffold_path

        print("!" * 80)
        from pprint import pprint
        pprint(scaffold_path)

        helix = scaffold_path[0]
        path = scaffold_path[1::]
        path.append(None)
        for next_helix in path:
            node = helix.node_to
            id_1 = node.helix_to_slot(helix) + 1
            id_2 = node.helix_to_slot(helix) - 1
            c_helix_1 = node.number_to_helix(id_1)
            c_helix_2 = node.number_to_helix(id_2)
            if c_helix_1 and c_helix_1 != next_helix:
                if c_helix_1.node_from == node:
                    print(helix.vvhelix_id, "->", c_helix_1.vvhelix_id)
                    design.append([c_helix_1.vvhelix_id, helix.vvhelix_id])
            if c_helix_2 and c_helix_2 != next_helix:
                if c_helix_2.node_from == node:
                    print(helix.vvhelix_id, "->", c_helix_2.vvhelix_id)
                    design.append([c_helix_2.vvhelix_id, helix.vvhelix_id])
            helix = next_helix

        print("-" * 80)
        print("final design is:")

        # TODO: CHECK THIS...
        from pprint import pprint

        print("*" * 80)
        pprint(design)
        print("*" * 80)

        # create caDNAno file
        # construct generator to produce meaningful helix positions
        helix_position = generate_even_helix_position_sq()
        helices = []
        hex_grid = self.ids.hex_grid
        n_helix = int(hex_grid.vvhelix_id / 2)  # reduce(max, map(max, design)) / 2 + 1
        # change to be reasonable
        for i in range(n_helix):
            c, r = next(helix_position)
            helices.append(
                    vhelix(num=2 * i,
                           column=c,
                           row=r,
                           segment_length=37,
                           overhang=3)
            )
        # interconnect the freshly generated helices
        interconnect_helices(helices)
        # break all staples in the middle
        for h in helices:
            break_staple(h, 27)
        # provide the linkage for the staples
        interconnect_staples(helices, design)

        # dump the json to a file
        cadnano_file = {
            "vstrands": helices,
            "name": "Created by M.Matthies"
        }
        import json
        with open(os.path.join(fpath, filename), "w+") as out_file:
            print(filename)
            out_file.write(json.dumps(cadnano_file))
            # self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load_design, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load_design(self, path, filename):
        hex_canvas = self.ids.hex_grid
        # with open(os.path.join(path, filename[0])) as in_file:
        with open(filename[0]) as in_file:
            in_des = eval(in_file.read())
        for helix_pair in in_des:
            node_from_id, node_to_id = helix_pair
            node_from = hex_canvas.grid[node_from_id[0]][node_from_id[1]]
            node_to = hex_canvas.grid[node_to_id[0]][node_to_id[1]]

            with node_from.canvas:
                Color(1, 1, 1, 1)
                Ellipse(pos=(node_from.center[0] - 6, node_from.center[1] - 6), size=(12, 12))
            with node_to.canvas:
                Color(1, 1, 1, 1)
                Ellipse(pos=(node_to.center[0] - 6, node_to.center[1] - 6), size=(12, 12))

            vvh = VVHelix(from_node=node_from, to_node=node_to, vvhelix_id=hex_canvas.vvhelix_id)
            hex_canvas.scaffold_path.append(vvh)
            hex_canvas.vvhelix_id += 2
            hex_canvas.add_widget(vvh)

        from pprint import pprint
        pprint(hex_canvas.scaffold_path)
        self.dismiss_popup()

    def show_save(self):
        content = SaveDialog(save=self.save_design, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save_design(self, path, filename):
        design_to_save = []
        for helix in self.ids.hex_grid.scaffold_path:
            entry = [helix.node_from.grid_id, helix.node_to.grid_id]
            design_to_save.append(entry)
        with open(os.path.join(path, filename), "w+") as out_file:
            out_file.write(str(design_to_save))
        self.dismiss_popup()

    def clear_canvas(self):
        hg = self.ids.hex_grid
        hg.clean()


class TriangularGrid(App):
    def build(self, *args):
        return MWindow()


if __name__ == '__main__':
    TriangularGrid(title="k-router").run()
