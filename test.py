#!/usr/bin/python3

import sys
import re
from time import sleep
from typing import Iterator, Tuple

lpr = open("/dev/usb/lp0", "r+b", buffering=0)

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

SPECIALS = {
    "NUL" : NUL,
    "OH"  : OH,
    "STX" : STX,
    "EXT" : EXT,
    "EOT" : EOT,
    "ENO" : ENO,
    "ACK" : ACK,
    "BEL" : BEL,
    "BS"  : BS,
    "HT"  : HT,
    "LF"  : LF,
    "VT"  : VT,
    "FF"  : FF,
    "CR"  : CR,
    "SO"  : SO,
    "SI"  : SI,
    "DLE" : DLE,
    "DC1" : DC1,
    "XON" : XON,
    "DC2" : DC2,
    "DC3" : DC3,
    "XOFF": XOFF,
    "DC4" : DC4,
    "NAK" : NAK,
    "SYN" : SYN,
    "ETB" : ETB,
    "CAN" : CAN,
    "EM"  : EM,
    "SUB" : SUB,
    "ESC" : ESC,
    "FS"  : FS,
    "GS"  : GS,
    "RS"  : RS,
    "US"  : US,
}

PRINT_TO_PAPER = ESC + b'c0\4'

# TOOLS

debug_mode = False

def send(*args):
    buffer = bytes()
    for a in args:
        if isinstance(a, bytes):
            buffer += a
        elif isinstance(a, str):
            buffer += a.encode("ascii")
        else:
            buffer += bytes([a])
    # if debug_mode:
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

def tokenize(input_line: str) -> Iterator[Tuple[bool, str]]:
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
            for is_str, token in tokenize(line):
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
    print("Printer model ID\n", dump(recv(1,2)))

    send(GS, b'I2')
    sleep(0.2)
    print("Printer type ID\n", dump(recv(1,2)))

    send(GS, b'I3')
    sleep(0.2)
    print("Printer Version ID\n", dump(recv(1,2)))

    for info in [ 33, 35, 36, 96, 110, 65, 66, 67, 68, 69, 111, 112 ]:
        send(GS, b'I', info)
        sleep(0.2)
        print(f"Information {info}\n", dump(recv(20,tries=2,until=0)))

def printer_counters():
    for counter in range(10, 80, 10):
        send(GS, b'g2\0', counter, 0)
        sleep(0.2)
        print(f"Counter {counter}\n", dump(recv(20,tries=2,until=0)))

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

LEFT_TO_RIGHT = 0
BOTTOM_TO_TOP = 1
RIGHT_TO_LEFT = 2
TOP_TO_BOTTOM = 3
PT_PER_MM = 5

# all dimension are given in mm and translated in point i inner code
class Page:
    # width and height are relative to page direction
    # thus with TOP_TO_BOTTOM and BOTTOM_TO_TOP directions, page width is paper height
    def __init__(self, width, height, direction=LEFT_TO_RIGHT):
        self.width = width
        self.height = height
        self.direction = direction
        self.x = 0
        self.y = 0

    def __enter__(self):
        self.prepare_page()
        return self

    def __exit__(self, e_type, e_value, e_stack):
        send(FF)
        reset()

    def prepare_page(self):
        # select paper, page mode, vertical text
        send(PRINT_TO_PAPER, ESC, 'L')
        # 0.2mm per point => 5 pt per mm
        send(GS, "P", 127, 127)
        if self.direction in (LEFT_TO_RIGHT, RIGHT_TO_LEFT):
            w = self.width * PT_PER_MM
            h = self.height * PT_PER_MM
        else:
            w = self.height * PT_PER_MM
            h = self.width * PT_PER_MM
        send(ESC, 'W', 0,0, 0,0 , w % 256, w >> 8, h % 256, h >> 8)
        # set direction
        send(ESC, 'T', self.direction)

    def _move_y(self, dir, value):
        while value > 255:
            send(ESC, dir, 255)
            value -= 255
        send(ESC, dir, value)

    # x, y are relative to page direction
    # thus with bottom to top page, x==0 is bottom border and y==0 is left border
    def print_at(self, text, x, y):
        x = int(x * 5)
        if self.x != x:
            send(ESC, '$', x % 256, x >> 8)
            self.x = x
        y = int(y * 5)
        if self.y < y:
            self._move_y('J', y - self.y)
            self.y = y
        elif self.y > y:
            self._move_y('K', y - self.y)
            self.y = y
        send(text)


def write_check(amount_digit, amount_letters, order, place, date, currency="€"):
    with Page(170, 80, TOP_TO_BOTTOM) as p:
        p.print_at(amount_letters, 3.5, 2)
        p.print_at(order, 2, 3)
        p.print_at(amount_digit, 13, 3)
        p.print_at(date, 13, 4)
        p.print_at(place, 13, 4.5)


def main(args):
    # status()
    # printer_info()
    # printer_counters()
    # beep(2)

    # data = parse_file("example.txt")
    # send(data)

    write_check(
        amount_digit="193.79",
        amount_letters="cent quatre vingt treize et soixante dix neuf centimes",
        order="pour ma pomme",
        place="Lille",
        date="25/12/2024"
    )

if __name__ == "__main__":
    main(sys.argv[1:])
