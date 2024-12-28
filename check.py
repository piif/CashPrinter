from time import sleep

import constants
from Printer import Printer
from Page import Page
from chars import *
from number import to_letters
from parser import dump

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

def write_check(printer: Printer, amount_digits, order, place, date, amount_letters=None, currency="€"):
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
    with Page(160, 80, direction=constants.PRINT_ORIENTATION["BOTTOM_TO_TOP"]) as page:
        page.print_at(amount_letters, 25, 20)
        if amount_letters2 is not None:
            page.print_at(amount_letters, 5, 26)
        page.print_at(order, 0, 35)
        page.print_at(amount_digits, 12, 32, size=constants.CHARACTER_SIZE["CHAR_DOUBLE"])
        page.print_at(date, 125, 41)
        page.print_at(place, 125, 48)
