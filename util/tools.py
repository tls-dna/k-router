"""
Works with the legacy version of caDNAno SQ
Works with even numbered helices, assumed they go all into one direction.
This simplifies the binding of the scaffold and binding of the staples
"""
MAX_ROWS = 20
MAX_COLS = 30
MAX_HELICES = MAX_ROWS * MAX_COLS


def generate_even_helix_position_sq(rows=MAX_ROWS, cols=MAX_COLS):
    """Iterator to generate the next even helix position on a square lattice.
    :param rows: number of rows in the lattice
    :param cols: number of columns in the lattice
    :return (row, col): tuple consisting of helix coordinates on the lattice
    """
    n_rows = rows * 2  # as the step is 2 we have to have double the number of rows
    for i in range(0, cols, 1):
        for j in range(0, n_rows, 2):
            m = 0 if i % 2 == 0 else 1  # to accommodate for the row shift at odd columns
            yield (i, j + m)


def vhelix(num=0, column=0, row=0, overhang=0, segment_length=26, displayed_length=126):
    """ Create a virtual helix.
    :param num: helix number
    :param column: helix column coordinate on square grid
    :param row: helix row coordinate on square grid
    :param overhang: length of the overhang
    :param segment_length: length of scaffold and staple strands on this segment
    :param displayed_length: displayed length in caDNAno
    :return: dictionary, containing virtual helix definition
    """
    return {
        "num": num,
        "col": column,
        "row": row,
        "loop": [0 for i in range(displayed_length)],
        "skip": [0 for i in range(displayed_length)],
        "stapLoop": [],
        "scafLoop": [],
        "stap": __staple(num=num, overhang=overhang, length=segment_length, displayed_length=displayed_length),
        "scaf": __scaffold(num=num, overhang=overhang, length=segment_length, displayed_length=displayed_length),
        "stap_colors": []
    }


def __scaffold(length=26, overhang=1, num=0, displayed_length=126):
    """Constructs scaffold segment for virtual helix.
    :param length: length of scaffold strand
    :param overhang: length of the overhang
    :param num: helix number
    :param displayed_length: displayed length in caDNAno
    :return: list containing scaffold base definitions
    """
    s = [[-1, -1, -1, -1] for i in range(overhang)]  # shift scaffold position overhang bases to the right
    s.append([-1, -1, num, overhang + 1])  # start base [-1,-1, num, base_number]
    s.extend([num, i - 1, num, i + 1]
             for i in range(overhang + 1, length + 2 * overhang - 1))  # construct scaffold path
    s.append([num, length + 2 * overhang + 2, -1, -1])  # last base [num, base_number, -1, -1]
    s.extend([[-1, -1, -1, -1]
              for i in range(displayed_length - length - 2 * overhang)])  # fill up displayed length
    return s


def __staple(length=26, overhang=1, num=0, displayed_length=126):
    """Constructs staple segment for virtual helix.
    :param length: length of staple strand on this segment
    :param overhang: length of the overhang
    :param num: helix number
    :param displayed_length: displayed length in caDNAno
    :return: list containing scaffold base definitions
    """
    s = [[num, 1, -1, -1]]  # start base, inverse as scaffold
    s.extend([num, i + 1, num, i - 1]
             for i in range(1, length - 1 + overhang))  # construct staple path
    s.append([-1, -1, num, length - 2 + overhang])  # end base
    s.extend([[-1, -1, -1, -1]
              for i in range(displayed_length - length - overhang)])  # fill up displayed length
    return s


def interconnect_helices(helices):
    """Interconnect scaffold path of helices in list.
    :param helices: list of helices
    """

    def bind_helix(h1, h2):
        """scaffold binding"""
        b1, b2 = None, None
        for b in h1["scaf"][::-1]:
            if b != [-1, -1, -1, -1]:
                b1 = b
                break
        for b in h2["scaf"]:
            if b != [-1, -1, -1, -1]:
                b2 = b
                break
        b1[2] = b2[2]
        b1[3] = b2[3] - 1  # don't ask me why ? ...
        b2[0] = b1[0]
        b2[1] = b1[1]

    for i in range(len(helices) - 1):
        bind_helix(helices[i], helices[i + 1])


def interconnect_staples(helices, connection_pairs):
    """Interconnect staple path, for given list of helices.
    :param helices: list of helices
    :param connection_pairs: list of  (helix number, helix number) which have to be connected
    """

    def connect_staples(h1, h2):
        """0->4 direction"""
        s1 = h1["stap"]
        s2 = h2["stap"]
        b1, b2 = None, None
        # b1 is always the first base
        b1 = s1[0]
        # b2 we have to search
        for b in s2[::-1]:
            if b != [-1, -1, -1, -1]:
                b2 = b
                break
        b1[2] = b2[2]
        b1[3] = b2[3] + 1  # don't ask me why ? ...
        b2[0] = b1[0]
        b2[1] = b1[1]

    # generate numbered dictionary
    helix_by_number = {}
    for h in helices:
        helix_by_number[h["num"]] = h
    for helix_numbers in connection_pairs:
        connect_staples(helix_by_number[helix_numbers[0]], helix_by_number[helix_numbers[1]])


def break_staple(helix, position=10):
    """Break a staple at given position.
    :param helix: location of the staple
    :param position: base position to place the nick
    """
    staple = helix["stap"]
    # staples start from 0, so position is the position of the nick
    b1 = staple[position]
    b2 = staple[position + 1]
    b1[0], b1[1] = -1, -1
    b2[2], b2[3] = -1, -1


COLOR_PALETTE = {
    "pink": 12060252,
    "black": 3355443,
    "gray": 8947848,
    "dark_red": 13369344,
    "light_red": 16204552,
    "orange": 16225054,
    "light_green": 11184640,
    "green": 5749504,
    "dark_green": 29184,
    "light_blue": 243362,
    "dark_blue": 1507550,
    "purple": 7536862,
}

def get_staple_ends(helix):
    """Provided a helix we get all the staple ends on that helix.
    :param helix: virtual helix
    :return: list of staple ends
    """
    stap = helix["stap"]
    ends = []
    for i, base in enumerate(stap):
        l, r = base[:2], base[2:4]
        if l == [-1, -1] and r != [-1, -1]:
            ends.append(i)
    return ends

def color_staple(staple_end, color, helix):
    """Color staple with corresponding color.
    :param staple_end: the start of the staple (5' end)
    :param color: color of the staple
    :param helix: location of staple end
    """
    helix["stap_colors"].append(
        [staple_end, color]
    )

