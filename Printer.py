import sys

from constants import *
from chars import *
from parser import dump

class Printer:
    def __init__(
            self,
            model: str,
            device: str = PRINTER_DEVICE,
            charset: str = DEFAULT_CHARSET,
            paper = PRINTER_OUTPUT["ROLL"],
            debug = False
    ):
        self.model = model
        self.specs = PRINTER_SPEC[model]
        self.device = device
        self.charset = CHARSETS[charset]
        self.debug = debug

        # open connection to printer
        self.lpr = open(self.device, "r+b", buffering=0)

        # reset + set charset and output
        self.reset()
        self.send(ESC, 't', self.charset)
        self.select_output(paper)


    def send(self, *args):
        buffer = bytes()
        for a in args:
            if isinstance(a, bytes):
                buffer += a
            elif isinstance(a, str):
                buffer += a.encode("cp1252")
            else:
                buffer += bytes([a])
        if self.debug:
            print(dump(buffer), file=sys.stderr)
        self.lpr.write(buffer)

    def recv(self, n, tries = 1, until=None):
        result = b''
        while tries > 0:
            result += self.lpr.read(n)
            n -= len(result)
            tries -= 1
            if len(result)>0 and until is not None and result[-1] == until:
                break
        return result

    def reset(self):
        self.send(ESC, b'@')

    def select_output(self, paper):
        self.paper = paper
        # select output for text and commands
        self.send(ESC, 'c0', self.paper, ESC, 'c1', self.paper)

    def print_image(self, data: list, direction = PRINT_ORIENTATION["LEFT_TO_RIGHT"]):
        horiz = direction in (PRINT_ORIENTATION["LEFT_TO_RIGHT"], PRINT_ORIENTATION["RIGHT_TO_LEFT"])
        # get DPI for "vertical" pixels depending on current printing direction
        dpi = self.specs["DPI"][self.paper][0 if horiz else 1]
        # deduce how many motion units required to move of 8 pixels = 1inch/dpi * 8 * motion_unit_per_mm
        spacing = round((25.4/dpi*8) * MU_MM)
        self.send(ESC, "3", spacing)
        # send each line of data
        for h in range(len(data)):
            l = len(data[h])
            self.send(ESC, "*", 0, l % 256, l >> 8, bytes(data[h]))
            self.send(LF)
        # go back to default line spacing
        self.send(ESC, "2")
