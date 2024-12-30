import re
from typing import Iterator, Tuple

from chars import *

def _tokenize(input_line: str) -> Iterator[Tuple[bool, str]]:
    # Regular expression to match either a quoted string or a word
    pattern = r'"([^"]*)"|(\S+)'
    
    # Find all matches in the input line
    for match in re.finditer(pattern, input_line):
        if match.group(1) is not None:  # Quoted string
            yield (True, match.group(1))
        elif match.group(2) is not None:  # Non-quoted word
            yield (False, match.group(2))

SPECIALS = {
    "NUL" : NUL,  "OH"  : OH,   "STX" : STX,  "EXT" : EXT,  "EOT" : EOT,  "ENO" : ENO,   "ACK" : ACK,  "BEL" : BEL,
    "BS"  : BS,   "HT"  : HT,   "LF"  : LF,   "VT"  : VT,   "FF"  : FF,   "CR"  : CR,    "SO"  : SO,   "SI"  : SI,
    "DLE" : DLE,  "DC1" : DC1,  "XON" : XON,  "DC2" : DC2,  "DC3" : DC3,  "XOFF": XOFF,  "DC4" : DC4,  "NAK" : NAK,
    "SYN" : SYN,  "ETB" : ETB,  "CAN" : CAN,  "EM"  : EM,   "SUB" : SUB,  "ESC" : ESC,   "FS"  : FS,   "GS"  : GS,
    "RS"  : RS,   "US"  : US
}

def parse_file(path):
    result = bytes()
    with open(path, "r") as f:
        for line in f.readlines():
            if line[0] == "'":
                continue
            result += parse_line(line)
    return result

def parse_line(line):
    result = bytes()
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


def dump(array):
    result = ""
    ascii = ""
    i=0
    for b in array:
        bb = bytes([b])
        result += f"{b:02X} "
        if bb in (ESC, GS, FF, LF):
            ascii += chr(0x2400 + b)
        elif b > 0x20 and b <= 0x80: # not in (0x81, 0x8D, 0x8F, 0x90, 0x9D)
            ascii += bb.decode("cp1252")
        else:
            ascii += '.'
        # ascii += bb.decode("cp1252") if b > 31 and b not in (0x81, 0x8D, 0x8F, 0x90, 0x9D) else '.'
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
