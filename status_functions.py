from time import sleep

from Printer import Printer
from chars import *
from parser import dump

def status(printer: Printer):
    printer.send(DLE, EOT, 1)
    sleep(0.2)
    print(printer.recv(1,2))

def printer_info(printer: Printer):
    printer.send(GS, b'I1')
    sleep(0.2)
    print("Printer model ID\n" + dump(printer.recv(1,2)))

    printer.send(GS, b'I2')
    sleep(0.2)
    print("Printer type ID\n" + dump(printer.recv(1,2)))

    printer.send(GS, b'I3')
    sleep(0.2)
    print("Printer Version ID\n" + dump(printer.recv(1,2)))

    for info in [ 33, 35, 36, 96, 110, 65, 66, 67, 68, 69, 111, 112 ]:
        printer.send(GS, b'I', info)
        sleep(0.2)
        print(f"Information {info}\n" + dump(printer.recv(20,tries=2,until=0)))

def printer_settings(printer: Printer):
    printer.send(GS, "(E", 2, 0, 6, 1)
    sleep(0.2)
    print("NV user memory\n" + dump(printer.recv(10,2,until=0)))

    printer.send(GS, "(E", 2, 0, 6, 2)
    sleep(0.2)
    print("NV bit image memory\n" + dump(printer.recv(10,2,until=0)))

    printer.send(GS, "(E", 2, 0, 6, 5)
    sleep(0.2)
    print("Print density\n" + dump(printer.recv(10,2,until=0)))

    printer.send(GS, "(E", 2, 0, 6, 118)
    sleep(0.2)
    print("Black color density\n" + dump(printer.recv(10,2,until=0)))
 
def printer_counters(printer: Printer):
    for counter in range(10, 80, 10):
        printer.send(GS, b'g2\0', counter, 0)
        sleep(0.2)
        print(f"Counter {counter}\n" + dump(printer.recv(20,tries=2,until=0)))
