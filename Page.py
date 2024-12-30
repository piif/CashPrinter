from Printer import Printer
from chars import *
from constants import *

# def to_x(x, paper = TO_PAPER):
#     return int(x * (MOTION_X_PAPER if paper == TO_PAPER else MOTION_X_ROLL) / 25.4)

# def to_y(y, paper):
#     return int(y * (MOTION_Y_PAPER if paper == TO_PAPER else MOTION_Y_ROLL) / 25.4)

# def to_char(x, direction = LEFT_TO_RIGHT, paper = TO_PAPER):
#     if direction in (LEFT_TO_RIGHT, RIGHT_TO_LEFT):
#         if paper == TO_PAPER:
#             ratio = CHAR_WIDTH_H_PAPER
#         else:
#             ratio = CHAR_WIDTH_H_ROLL
#     else:
#         if paper == TO_PAPER:
#             ratio = CHAR_WIDTH_V_PAPER
#         else:
#             ratio = CHAR_WIDTH_V_ROLL
#     return int(x/ratio)

# all dimension are given in mm and translated in point in inner code
class Page:
    # width and height are in mm and relative to page direction
    # thus with TOP_TO_BOTTOM and BOTTOM_TO_TOP directions, page width is paper height
    def __init__(self, printer: Printer, width, height, direction=PRINT_ORIENTATION["LEFT_TO_RIGHT"]):
        self.printer = printer
        self.width = width
        self.height = height
        self.paper = self.printer.paper

        self.direction = direction
        self.printer.send(ESC, 'T', self.direction)
        self.prepare_page()

    def __enter__(self):
        return self

    def __exit__(self, e_type, e_value, e_stack):
        self.flush()

    def flush(self):
        self.printer.send(ESC, FF, CAN)
        self.printer.reset()

    def prepare_page(self):
        # select paper, page mode
        self.printer.send(ESC, 'c0', self.paper, ESC, 'c1', self.paper, ESC, 'L')
        # 0.1mm per point
        self.printer.send(GS, 'P', 254, 254)

        max_width = self.printer.specs["WIDTH"][self.paper]
        self.horiz = self.direction in (PRINT_ORIENTATION["LEFT_TO_RIGHT"], PRINT_ORIENTATION["RIGHT_TO_LEFT"])

        if self.horiz:
            self.width = min(self.width, max_width)
        else:
            self.width = min(self.height, max_width)

        self.left = 0
        # if paper output, must justify on the right
        if self.paper in (PRINTER_OUTPUT["PAPER"], PRINTER_OUTPUT["VALIDATION"]): # or BACK_PAPER ??
            if self.horiz:
                self.left = max_width - self.width
            else:
                self.left = max_width - self.height

    # x, y are relative to page direction
    # thus with bottom to top page, x==0 is bottom border and y==0 is left border
    def print_at(self, x, y, text: str = None, size = CHARACTER_SIZE["CHAR_SINGLE"]):
        x = min(x, self.width)
        y = min(y, self.height)

        if self.direction == PRINT_ORIENTATION["LEFT_TO_RIGHT"]:
            w, h = self.width - x , self.height - y
            x += self.left
        elif self.direction == PRINT_ORIENTATION["RIGHT_TO_LEFT"]:
            w, h = self.width - x, self.height - y
            x, y = self.left, 0
        elif self.direction == PRINT_ORIENTATION["TOP_TO_BOTTOM"]:
            w, h = self.height - y, self.width - x
            x, y = self.left, x
        elif self.direction == PRINT_ORIENTATION["BOTTOM_TO_TOP"]:
            w, h = self.height - y, self.width - x
            x, y = self.left, 0

        x *= 10
        y *= 10
        w *= 10
        h *= 10

        self.printer.send(ESC, 'W', x % 256, x >> 8, y % 256, y >> 8 , w % 256, w >> 8, h % 256, h >> 8)

        if str is not None:
            self.printer.send(GS, '!', size, text, GS, '!', CHARACTER_SIZE["CHAR_SINGLE"])
