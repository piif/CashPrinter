from time import sleep
import sys

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

def send(*args):
    lpr.write(b''.join([ b if isinstance(b, bytes) else bytes([b]) for b in args ]))

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
        ascii += chr(b) if b > 15 else '.'
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
    # marche pas ?
    send(ESC, b'(A', 4, 0, 48, mode, 2, 2)

def parse_file(path):
    result = bytes()
    with open(path, "r") as f:
        for line in f.readlines():
            if line[0] == "'":
                continue
            looking_eos = False
            for token in line.split():
                print(f"<{token}>, {looking_eos}")
                if looking_eos:
                    if token.endswith('"'):
                        result += bytes(token[:-1], "ascii")
                        looking_eos = False
                    else:
                        result += bytes(token, "ascii")
                elif token.startswith('"'):
                    if len(token)>1 and token.endswith('"'):
                        result += bytes(token[1:-1], "ascii")
                    else:
                        result += bytes(token[1:], "ascii")
                        looking_eos = True
                elif token in SPECIALS:
                    result += SPECIALS[token]
                elif token.startswith("0x"):
                    result += bytes([ int(token[2:], 16) ])
                else:
                    result += bytes([ int(token) ])
    return result


def main(args):
    # status()
    # printer_info()
    # printer_counters()
    # beep(2)
    parse_file("sample.txt")

if __name__ == "__main__":
    main(sys.argv[1:])
