from time import sleep

import constants
from Printer import Printer
from Page import Page
from chars import *
from number import to_letters
from parser import dump
from data import FCPE_48x40

def read_check(printer: Printer):
    printer.send(FS, b'a0', 1)
    _parse_check()

def reread_check(printer: Printer):
    printer.send(FS, b'b')
    _parse_check()

def eject_check(printer: Printer):
    printer.send(FS, b'a2')

def prepare_check_print(printer: Printer):
    printer.send(FS, b'a1')

def _parse_check(printer: Printer):
    for retry in range(1,10):
        print(".")
        sleep(2)
        result = printer.recv(40,until = 0)
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


def convert_amount(amount_digits, amount_letters=None, currency=("€", "euro", "euros")):
    if amount_letters is None:
        amount_letters = to_letters(amount_digits, currency[1:])

    amount_digits = str(amount_digits)
    if '.' in amount_digits:
        amount_digits = amount_digits.replace('.', currency[0])
    else:
        amount_digits += currency[0]

    return amount_digits, amount_letters


def write_check(printer: Printer, amount_digits, order, place, date, amount_letters=None, currency=("€", "euro", "euros")):
    amount_digits, amount_letters = convert_amount(amount_digits, amount_letters, currency)

    if len(amount_letters) > 35:
        limit = amount_letters.rfind(' ', 0, 35)
        amount_letters2 = amount_letters[limit+1:]
        amount_letters = amount_letters[:limit]
    else:
        amount_letters2 = None

    with Page(printer, 160, 80, direction=constants.PRINT_ORIENTATION["BOTTOM_TO_TOP"]) as page:
        page.print_at( 25, 20, amount_letters)
        if amount_letters2 is not None:
            page.print_at(5, 26, amount_letters)
        page.print_at(  0, 35, order)
        page.print_at( 12, 32, amount_digits, size=constants.CHARACTER_SIZE["CHAR_DOUBLE"])
        page.print_at(125, 41, date)
        page.print_at(125, 48, place)


def write_receipt(printer: Printer, amount_digits, order, date, reference, amount_letters=None, currency=("€", "euro", "euros")):
    amount_digits, amount_letters = convert_amount(amount_digits, amount_letters, currency)

    with Page(printer, 78, 80) as page:
        page.print_at(0,  0, "- "*20)
        page.print_at(0,  8, f"Reçu N° {reference}")
        page.print_at(0, 10, "L'association FCPE Baggio",)
        page.print_at(5, 28, "Atteste avoir reçu",)
        page.print_at(0, 38, "De {order}")
        page.print_at(0, 46, f"La somme de {amount_digits} ,")
        page.print_at(0, 54, amount_letters, currency[1:])
        page.print_at(0, 62, f"Le {date}")
        page.print_at(0, 70, "- "*20)
        printer.send(LF)
        printer.print_image(data = FCPE_48x40.IMAGE_DATA, indent=1)
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
