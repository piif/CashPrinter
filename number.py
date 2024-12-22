# conversion de nombres en lettres, en français

from decimal import Decimal

TESTS = [
    (0, 'zéro euro'),
    (1, 'un euro'),
    (12, 'douze euros'),
    (17.08, 'dix-sept euros et huit centimes'),
    (21, 'vingt et un euros'),
    (27, 'vingt sept euros'),
    (100, 'cent euros'),
    (200, 'deux cents euros'),
    (123, 'cent vingt trois euros'),
    (321, 'trois cent vingt et un euros'),
    (123.45, 'cent vingt trois euros et quarante cinq centimes'),
    (1000, 'mille euros'),
    (2000, 'deux mille euros'),
    (2020, 'deux mille vingt euros'),
    (1000.01, 'mille euros et un centime'),
    (2000.19, 'deux mille euros et dix-neuf centimes'),
    (2074.12, 'deux mille soixante quatorze euros et douze centimes'),
    (987654, 'neuf cent quatre vingt sept mille six cent cinquante quatre euros'),
    (898898.99, 'huit cent quatre vingt dix-huit mille huit cent quatre vingt dix-huit euros et quatre vingt dix-neuf centimes'),
]

def tests():
    for (value, expected) in TESTS:
        result = to_letters(value, ('euro', 'euros'), ('centime', 'centimes'))
        if result == expected:
            print(f"OK   {value} / {result}")
        else:
            print(f"FAIL {value} / {result} != {expected}")

CHIFFRES = [
    "zéro", "un", "deux", "trois", "quatre",
    "cinq", "six", "sept", "huit", "neuf",
    "dix", "onze", "douze", "treize", "quatorze",
    "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"
]
DIZAINES = [ None, None, "vingt", "trente", "quarante", "cinquante", "soixante", None, "quatre vingt", None ]
CENT = [ "cent", "cents" ]
MILLE = "mille"
ET = "et"

def raw_to_letters(value):
    if value >= 100:
        centaines = int(value / 100)
        reste = value % 100
        if centaines == 1:
            if reste == 0:
                return CENT[0]
            else:
                return f"{CENT[0]} {raw_to_letters(reste)}"
        else:
            if reste == 0:
                return f"{CHIFFRES[centaines]} {CENT[1]}"
            else:
                return f"{CHIFFRES[centaines]} {CENT[0]} {raw_to_letters(reste)}"

    if value < 20:
        return CHIFFRES[value]
    dizaines = int(value / 10)
    unites = value % 10

    if dizaines < 7:
        if unites == 1:
            return f"{DIZAINES[dizaines]} {ET} {CHIFFRES[unites]}"
        elif unites == 0:
            return f"{DIZAINES[dizaines]}"
        else:
            return f"{DIZAINES[dizaines]} {CHIFFRES[unites]}"
    else:
        if dizaines == 7 or dizaines == 9:
            dizaines -= 1
            unites += 10
        return f"{DIZAINES[dizaines]} {CHIFFRES[unites]}"

def to_letters(value, unit='', subunit=''):
    milliers = int(value / 1000)
    unites = int(value) % 1000
    centimes = int(Decimal(str(value)) * 100) % 100

    if isinstance(unit, tuple):
        if value > 1:
            unit = unit[1]
        else:
            unit = unit[0]
    if isinstance(subunit, tuple):
        if centimes > 1:
            subunit = subunit[1]
        else:
            subunit = subunit[0]

    if milliers == 0:
        if unites == 0:
            if centimes == 0:
                return f"{CHIFFRES[0]} {unit}"
            else:
                return f"{raw_to_letters(centimes)} {subunit}"
        else:
            if centimes == 0:
                return f"{raw_to_letters(unites)} {unit}"
            else:
                return f"{raw_to_letters(unites)} {unit} {ET} {raw_to_letters(centimes)} {subunit}"
    else:
        if milliers == 1:
            result = MILLE
        else:
            result = f"{raw_to_letters(milliers)} {MILLE}"
        if unites == 0:
            result += f" {unit}"
        else:
            result += f" {raw_to_letters(unites)} {unit}"
        if centimes != 0:
            result += f" {ET} {raw_to_letters(centimes)} {subunit}"
        return result


if __name__ == "__main__":
    tests()
