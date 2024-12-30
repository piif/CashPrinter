#!/usr/bin/python3

import sys
import re
from time import sleep
from getopt import getopt, GetoptError

from Printer import Printer
from Page import Page
from number import to_letters
from chars import *
from constants import *
from parser import dump, parse_file, parse_line

from payment import *
from status_functions import *

from data import FCPE_48x40

# does not work : no buzzer on my model
def beep(printer: Printer, mode):
    printer.send(ESC, b'(A', 4, 0, 48, mode, 2, 2)


def test_pages(printer):
    pg = Page(printer, 60, 70, constants.PRINT_ORIENTATION["LEFT_TO_RIGHT"])
    pg.print_at(0,0, "L2R")
    for i in range(5):
        pg.print_at(i*10,8, "|>")
    pg.print_at(0,70, "_L2R_")
    pg.print_at(0,62, "_L2R_-8")

    pg = Page(printer, 60, 70, constants.PRINT_ORIENTATION["RIGHT_TO_LEFT"])
    pg.print_at(0,0, "R2L")
    for i in range(5):
        pg.print_at(i*10,8, "|<")

    pg = Page(printer, 70, 60, constants.PRINT_ORIENTATION["TOP_TO_BOTTOM"])
    pg.print_at(0,0, "T2B")
    for i in range(5):
        pg.print_at(i*10,8, "|v")

    pg = Page(printer, 70, 60, constants.PRINT_ORIENTATION["BOTTOM_TO_TOP"])
    pg.print_at(0,0, "B2T")
    for i in range(5):
        pg.print_at(i*10,8, "|^")

    pg.flush()

def main(args):
    model = "TM-H6000-III"
    debug = False
    device = "/dev/usb/lp0"
    output = None
    test=None

    try:
        opts, args = getopt(args, "dD:M:T:O:", ["debug", "device=", "model=", "test=", "output="])
    except GetoptError as err:
        print(err)
        sys.exit(2)

    for o, a in opts:
        if o in ("-d", "--debug"):
            debug = True
        elif o in ("-D", "--device"):
            device = a
        elif o in ("-M", "--model"):
            model = a
        elif o in ("-T", "--test"):
            test = a
        elif o in ("-O", "--output"):
            output = a
        else:
            raise ValueError(f"unhandled option {o}")

    if output is None or output == "roll":
        paper = constants.PRINTER_OUTPUT["ROLL"]
    elif output == "paper":
        paper = constants.PRINTER_OUTPUT["PAPER"]
    else:
        raise ValueError(f"unknown output {output} (must be ROLL or PAPER)")

    printer = Printer(model = model, debug = debug, device = device, paper = paper)

    if test is None:
        pass
    elif test == "status":
        status(printer)
    elif test == "printer_info":
        printer_info(printer)
    elif test == "printer_counters":
        printer_counters(printer)
    elif test == "beep":
        beep(printer, 2)
    elif test == "christmas":
        data = parse_file("data/christmas_coupon.txt")
        printer.send(data)
    elif test == "write_check":
        write_check(printer,
            amount_digits=193.79,
            # amount_letters="cent quatre vingt treize euros et soixante dix neuf centimes",
            order="pour ma pomme",
            place="Lille",
            date="25/12/2024"
        )
    elif test == "image":
        printer.print_image(data = FCPE_48x40.IMAGE_DATA)
        # printer.send(FF)
    elif test == "pages":
        test_pages(printer)
    elif test == "write_receipt":
        write_receipt(printer, 20, "Monsieur Quelqu'un", "25/12/2024", "2024_042")

    if len(args) > 0:
        data = parse_line(" ".join(args))
        printer.send(data)

    # reset()
    # printer.send('12345678901234567890123456789012345678901234567890')
    # printer.send(LF)


if __name__ == "__main__":
    main(sys.argv[1:])
