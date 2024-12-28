#!/usr/bin/python3

import sys
import re
from time import sleep

from Printer import Printer
from Page import Page
from number import to_letters
from chars import *
from constants import *
from parser import dump, parse_file

from check import *
from status_functions import *

import data.FCPE_48x40

# does not work : no buzzer on my model
def beep(printer: Printer, mode):
    printer.send(ESC, b'(A', 4, 0, 48, mode, 2, 2)


def write_receipt(printer: Printer, amount_digits, order, date, reference, amount_letters=None, currency="€"):
    with Page(78, 80, paper=PRINTER_OUTPUT["ROLL"]) as page:
        printer.send("- "*20)
        page.print_at("- "*20, 0, 0)
        page.print_at(f"Reçu N° {reference}", 0, 8)
        page.print_at("L'association FCPE Baggio", 20, 10)
        page.print_at("Atteste avoir reçu", 15, 28)
        page.print_at("De {order}", 0, 38)
        page.print_at("La somme de :", 0, 46)
        page.print_at(amount_letters, 0, 54)
        page.print_at(f"Le {date}", 0, 62)
        page.print_at("- "*20, 0, 70)
        printer.send(LF)
        printer.print_image(data = data.FCPE_48x40.IMAGE_DATA, indent=1)


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

def main(args):
    printer = Printer(model = "TM-H6000-III", debug = True)

    # status(printer)
    # printer_info(printer)
    # printer_counters(printer)
    # beep(printer, 2)

    # data = parse_file("example.txt")
    # printer.send(data)

    # write_check(printer,
    #     amount_digits=193.79,
    #     # amount_letters="cent quatre vingt treize et soixante dix neuf centimes",
    #     order="pour ma pomme",
    #     place="Lille",
    #     date="25/12/2024"
    # )

    printer.select_output(constants.PRINTER_OUTPUT["PAPER"])
    printer.print_image(data = data.FCPE_48x40.IMAGE_DATA)
    printer.send(FF)

    # reset()
    # printer.send('12345678901234567890123456789012345678901234567890')
    # printer.send(LF)

    # write_receipt(printer, 20, "Monsieur Quelqu'un", "25/10/2024", "2024_42")

if __name__ == "__main__":
    main(sys.argv[1:])
