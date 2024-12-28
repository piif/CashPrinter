#!/usr/bin/python3

import sys
import re
from time import sleep
from typing import Iterator, Tuple

from number import to_letters
import data.FCPE_48x40

# ascii command codes

NUL = b'\x00'
OH  = b'\x01'
STX = b'\x02'
EXT = b'\x03'
EOT = b'\x04'
ENO = b'\x05'
ACK = b'\x06'
BEL = b'\x07'
BS  = b'\x08'
HT  = b'\x09'
LF  = b'\x0A'
VT  = b'\x0B'
FF  = b'\x0C'
CR  = b'\x0D'
SO  = b'\x0E'
SI  = b'\x0F'
DLE = b'\x10'
DC1 = b'\x11'
XON = DC1
DC2 = b'\x12'
DC3 = b'\x13'
XOFF = DC3
DC4 = b'\x14'
NAK = b'\x15'
SYN = b'\x16'
ETB = b'\x17'
CAN = b'\x18'
EM  = b'\x19'
SUB = b'\x1A'
ESC = b'\x1B'
FS  = b'\x1C'
GS  = b'\x1D'
RS  = b'\x1E'
US  = b'\x1F'

EURO = b'\xd5'

SPECIALS = {
    "NUL" : NUL,  "OH"  : OH,   "STX" : STX,  "EXT" : EXT,  "EOT" : EOT,  "ENO" : ENO,   "ACK" : ACK,  "BEL" : BEL,
    "BS"  : BS,   "HT"  : HT,   "LF"  : LF,   "VT"  : VT,   "FF"  : FF,   "CR"  : CR,    "SO"  : SO,   "SI"  : SI,
    "DLE" : DLE,  "DC1" : DC1,  "XON" : XON,  "DC2" : DC2,  "DC3" : DC3,  "XOFF": XOFF,  "DC4" : DC4,  "NAK" : NAK,
    "SYN" : SYN,  "ETB" : ETB,  "CAN" : CAN,  "EM"  : EM,   "SUB" : SUB,  "ESC" : ESC,   "FS"  : FS,   "GS"  : GS,
    "RS"  : RS,   "US"  : US,   "EURO": EURO
}

# TOOLS

debug_mode = True

def send(*args):
    buffer = bytes()
    for a in args:
        if isinstance(a, bytes):
            buffer += a
        elif isinstance(a, str):
            buffer += a.encode("cp1252")
        else:
            buffer += bytes([a])
    if debug_mode:
        print(dump(buffer), file=sys.stderr)
    lpr.write(buffer)

def recv(n, tries = 1, until=None):
    result = b''
    while tries > 0:
        result += lpr.read(n)
        n -= len(result)
        tries -= 1
        if len(result)>0 and until is not None and result[-1] == until:
            break
    return result

def dump(array):
    result = ""
    ascii = ""
    i=0
    for b in array:
        result += f"{b:02X} "
        ascii += chr(b) if b > 31 else '.'
        i += 1
        if i == 8:
            result += " "
            ascii += " "
        elif i == 16:
            result += f"  {ascii}\n"
            i = 0
            ascii = ""
    if i != 0:
        result += "   " * (16-i)
        if i < 8:
            result += " "
        result += f"  {ascii}\n"
    return result

def _tokenize(input_line: str) -> Iterator[Tuple[bool, str]]:
    # Regular expression to match either a quoted string or a word
    pattern = r'"([^"]*)"|(\S+)'
    
    # Find all matches in the input line
    for match in re.finditer(pattern, input_line):
        if match.group(1) is not None:  # Quoted string
            yield (True, match.group(1))
        elif match.group(2) is not None:  # Non-quoted word
            yield (False, match.group(2))

def parse_file(path):
    result = bytes()
    with open(path, "r") as f:
        for line in f.readlines():
            if line[0] == "'":
                continue
            for is_str, token in _tokenize(line):
                if is_str:
                    result += bytes(token, "ascii")
                elif token in SPECIALS:
                    result += SPECIALS[token]
                elif token.startswith("0x"):
                    result += bytes([ int(token[2:], 16) ])
                else:
                    result += bytes([ int(token) ])
    return result

# COMMANDS

def reset():
    send(ESC, b'@')

def status():
    send(DLE, EOT, 1)
    sleep(0.2)
    print(recv(1,2))

def printer_info():
    send(GS, b'I1')
    sleep(0.2)
    print("Printer model ID\n" + dump(recv(1,2)))

    send(GS, b'I2')
    sleep(0.2)
    print("Printer type ID\n" + dump(recv(1,2)))

    send(GS, b'I3')
    sleep(0.2)
    print("Printer Version ID\n" + dump(recv(1,2)))

    for info in [ 33, 35, 36, 96, 110, 65, 66, 67, 68, 69, 111, 112 ]:
        send(GS, b'I', info)
        sleep(0.2)
        print(f"Information {info}\n" + dump(recv(20,tries=2,until=0)))

def printer_settings():
    send(GS, "(E", 2, 0, 6, 1)
    sleep(0.2)
    print("NV user memory\n" + dump(recv(10,2,until=0)))

    send(GS, "(E", 2, 0, 6, 2)
    sleep(0.2)
    print("NV bit image memory\n" + dump(recv(10,2,until=0)))

    send(GS, "(E", 2, 0, 6, 5)
    sleep(0.2)
    print("Print density\n" + dump(recv(10,2,until=0)))

    send(GS, "(E", 2, 0, 6, 118)
    sleep(0.2)
    print("Black color density\n" + dump(recv(10,2,until=0)))
 
def printer_counters():
    for counter in range(10, 80, 10):
        send(GS, b'g2\0', counter, 0)
        sleep(0.2)
        print(f"Counter {counter}\n" + dump(recv(20,tries=2,until=0)))

def beep(mode):
    # does not work : no buzzer on my model
    send(ESC, b'(A', 4, 0, 48, mode, 2, 2)

def read_check():
    send(FS, b'a0', 1)
    _parse_check()

def reread_check():
    send(FS, b'b')
    _parse_check()

def eject_check():
    send(FS, b'a2')

def prepare_check_print():
    send(FS, b'a1')

def _parse_check():
    for retry in range(1,10):
        print(".")
        sleep(2)
        result = recv(40,until = 0)
        if len(result) > 0:
            break
    print("Result")
    print(dump(result))
    if result[0] != 0x5F: # '_'
        print(f"header error ({result[0]})")
        return None
    if result[1] & 0x20 == 0x20:
        print("read error")
        return None
    return result[2:-1].decode("ascii")

# printer destinations and width
TO_ROLL = 3
ROLL_WIDTH = 71

TO_PAPER = 4
PAPER_WIDTH = 90

# print orientation
LEFT_TO_RIGHT = 0
BOTTOM_TO_TOP = 1
RIGHT_TO_LEFT = 2
TOP_TO_BOTTOM = 3

# dot/characters dimensions
MOTION_X_PAPER = 160 # horiz motion unit = 1" / MOTION_X
MOTION_Y_PAPER = 144 # vert motion unit = 1" / MOTION_Y
MOTION_X_ROLL  = 180
MOTION_Y_ROLL  = 360
CHAR_WIDTH_H_PAPER = 76/40 # width of a char printed horizontaly
CHAR_WIDTH_V_PAPER = 105/50 # width of a char printed verticaly
CHAR_WIDTH_H_ROLL  = 71/42
CHAR_WIDTH_V_ROLL  = 84/50

# character size
CHAR_SINGLE = b'\x00'
CHAR_DOUBLE_WIDTH = b'\x10'
CHAR_DOUBLE_HEIGHT = b'\x01'
CHAR_DOUBLE = b'\x11'

def to_x(x, paper = TO_PAPER):
    return int(x * (MOTION_X_PAPER if paper == TO_PAPER else MOTION_X_ROLL) / 25.4)

def to_y(y, paper):
    return int(y * (MOTION_Y_PAPER if paper == TO_PAPER else MOTION_Y_ROLL) / 25.4)

def to_char(x, direction = LEFT_TO_RIGHT, paper = TO_PAPER):
    if direction in (LEFT_TO_RIGHT, RIGHT_TO_LEFT):
        if paper == TO_PAPER:
            ratio = CHAR_WIDTH_H_PAPER
        else:
            ratio = CHAR_WIDTH_H_ROLL
    else:
        if paper == TO_PAPER:
            ratio = CHAR_WIDTH_V_PAPER
        else:
            ratio = CHAR_WIDTH_V_ROLL
    return int(x/ratio)

# all dimension are given in mm and translated in point in inner code
class Page:
    # width and height are relative to page direction
    # thus with TOP_TO_BOTTOM and BOTTOM_TO_TOP directions, page width is paper height
    def __init__(self, width, height, paper=TO_PAPER, direction=LEFT_TO_RIGHT):
        self.width = width
        self.height = height
        self.paper = paper
        self.direction = direction
        self.x = 0
        self.y = 0

        self.prepare_page()

    def __enter__(self):
        return self

    def __exit__(self, e_type, e_value, e_stack):
        send(ESC, FF, CAN)
        reset()

    def prepare_page(self):
        # select paper, page mode
        send(ESC, 'c0', self.paper, ESC, 'L')
        # # 0.2mm per point => 5 pt per mm : couldn't make it work
        # send(GS, "P", 127, 127)

        if self.direction in (LEFT_TO_RIGHT, RIGHT_TO_LEFT):
            w = to_x(self.width, self.paper)
            h = to_y(self.height, self.paper)
        else:
            w = to_x(self.height, self.paper)
            h = to_y(self.width, self.paper)

        if self.paper == TO_PAPER:
            max_w = to_x(PAPER_WIDTH, self.paper)
        else:
            max_w = to_x(ROLL_WIDTH, self.paper)
        if w > max_w:
            left = 0
            w = max_w
        else:
            left = max_w - w

        send(ESC, 'W', left % 256, left >> 8, 0,0 , w % 256, w >> 8, h % 256, h >> 8)

        # set direction
        send(ESC, 'T', self.direction)

    def set_direction(self, direction):
        self.direction = direction
        send(ESC, 'T', self.direction)

    def _move_y(self, dir, value):
        while value > 255:
            send(ESC, dir, 255)
            value -= 255
        send(ESC, dir, value)

    # x, y are relative to page direction
    # thus with bottom to top page, x==0 is bottom border and y==0 is left border
    def print_at(self, text, x, y, size = CHAR_SINGLE):
        indent = b' ' * to_char(x, self.direction)
        y = to_y(y, to_y)
        if self.y < y:
            self._move_y('J', y - self.y)
            self.y = y
        elif self.y > y:
            self._move_y('K', self.y - y)
            self.y = y
        send(indent, GS, '!', size, text, GS, '!', CHAR_SINGLE)


def write_check(amount_digits, order, place, date, amount_letters=None, currency="€"):
    if amount_letters is None:
        amount_letters = to_letters(amount_digits)
    amount_digits = str(amount_digits)
    if '.' in amount_digits:
        amount_digits = amount_digits.replace('.', currency)
    else:
        amount_digits += currency
    if len(amount_letters) > 35:
        limit = amount_letters.rfind(' ', 0, 35)
        amount_letters2 = amount_letters[limit+1:]
        amount_letters = amount_letters[:limit]
    else:
        amount_letters2 = None
    with Page(160, 80, direction=BOTTOM_TO_TOP) as p:
        p.print_at(amount_letters, 25, 20)
        if amount_letters2 is not None:
            p.print_at(amount_letters, 5, 26)
        p.print_at(order, 0, 35)
        p.print_at(amount_digits, 12, 32, size=CHAR_DOUBLE)
        p.print_at(date, 125, 41)
        p.print_at(place, 125, 48)


def write_receipt(amount_digits, order, date, reference, amount_letters=None, currency="€"):
    with Page(78, 50, paper=TO_ROLL) as p:
        send("- "*20, LF)
        p.print_at("- "*20, 0, 0)
        p.print_at(f"Reçu N° {reference}", 0, 8)
        send(LF)
        image(data = data.FCPE_48x40.IMAGE_DATA, indent=1)
        p.print_at("L'association FCPE Baggio", 20, 10)
        p.print_at("Atteste avoir reçu", 15, 28)
        p.print_at("De {order}", 0, 38)
        p.print_at("La somme de :", 0, 46)
        p.print_at(amount_letters, 0, 54)
        p.print_at(f"Le {date}", 0, 62)
        p.print_at("- "*20, 0, 70)


    # -------------------
    # Reçu N° {reference}
    # logo
    # L'association FCPE Baggio
    # Atteste avoir reçu de
    # {order}
    # La somme de {amount_letters}
    # <double>{amount_digits}
    # Le {date}
    # -------------------
    # 8<
    # -------------------
    # Reçu N° {reference}
    # logo
    # L'association FCPE Baggio
    # Atteste avoir reçu de
    # {order}
    # La somme de {amount_letters}
    # <double>{amount_digits}
    # Le {date}
    # -------------------
    # 8<
    pass

def select_output(paper):
    send(ESC, 'c0', paper, ESC, 'c1', paper)

def image(data: list, indent=0):
    send(ESC, "3", 24, ' '*indent)
    for h in range(len(data)):
        send(indent, ESC, "*", 0, len(data[h]), 0, bytes(data[h]))
        send(LF)
    send(ESC, "2")

def main(args):

    # status()
    # printer_info()
    # printer_counters()
    # beep(2)

    # data = parse_file("example.txt")
    # send(data)

    # write_check(
    #     amount_digits=193.79,
    #     # amount_letters="cent quatre vingt treize et soixante dix neuf centimes",
    #     order="pour ma pomme",
    #     place="Lille",
    #     date="25/12/2024"
    # )

    # select_output(TO_ROLL)
    # image(data = data.FCPE_48x40.IMAGE_DATA)
    # # send(FF)

    # reset()
    # send('12345678901234567890123456789012345678901234567890')
    # send(LF)
    write_receipt(20, "Monsieur Quelqu'un", "25/10/2024", "2024_42")

# open connection to printer
lpr = open("/dev/usb/lp0", "r+b", buffering=0)
# set char table 16 = WPC1252 with euro symbol at 0x80
send(ESC, 't', 16)

if __name__ == "__main__":
    main(sys.argv[1:])
