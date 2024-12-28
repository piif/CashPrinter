
PRINTER_DEVICE = "/dev/usb/lp0"
CHARSETS = {
    "PC437": 0,
    "Katakana": 1,
    "PC850"   : 2, # Multilingual
    "PC860"   : 3, # Portuguese
    "PC863"   : 4, # Canadian-French
    "PC865"   : 5, # Nordic
    "Hiragana": 6,
    "Kanji_1" : 7,
    "Kanji_2" : 8,
    "WPC1252" : 16, # Windows CP1252 with euro
    "PC866"   : 17, # Cyrillic
    "PC862"   : 18, # Latin2
    "PC858"   : 19, # Euro
    "Thai_42" : 20, # Thai Character Code 42
    "Thai_11" : 21, # Thai Character Code 11
    "Thai_13" : 22, # Thai Character Code 13
    "Thai_14" : 23, # Thai Character Code 14
    "Thai_16" : 24, # Thai Character Code 16
    "Thai_17" : 25, # Thai Character Code 17
    "Thai_18" : 26, # Thai Character Code 18
}
DEFAULT_CHARSET = "WPC1252" # named WPC1252 in documentation = CP1252, with € at 0x80

# printer outputs
PRINTER_OUTPUT = {
    "ROLL"       : 0x03,
    "PAPER"      : 0x04,
    "VALIDATION" : 0x08,
    "BACK_PAPER" : 0x40
}

# print orientation
PRINT_ORIENTATION = {
    "LEFT_TO_RIGHT": 0,
    "BOTTOM_TO_TOP": 1,
    "RIGHT_TO_LEFT": 2,
    "TOP_TO_BOTTOM": 3
}

# character size
CHARACTER_SIZE = {
    "CHAR_SINGLE"       : 0x00,
    "CHAR_DOUBLE_WIDTH" : 0x10,
    "CHAR_DOUBLE_HEIGHT": 0x01,
    "CHAR_DOUBLE"       : 0x11
}
# printer specific values
PRINTER_SPEC = {
    "TM-H6000-III": {
        "WIDTH" : {
            PRINTER_OUTPUT["ROLL"]       : 71,
            PRINTER_OUTPUT["PAPER"]      : 90,
            PRINTER_OUTPUT["VALIDATION"] : 90,
            PRINTER_OUTPUT["BACK_PAPER"] : 90
        },
        "DPI" : {
            PRINTER_OUTPUT["ROLL"]       : (60, 90), # vertical, horizontal
            PRINTER_OUTPUT["PAPER"]      : (72, 80),
            PRINTER_OUTPUT["VALIDATION"] : (72, 80),
            PRINTER_OUTPUT["BACK_PAPER"] : (72, 80)
        },

        # dot/characters dimensions
        "MOTION_X_PAPER": 160, # horiz motion unit = 1" / MOTION_X
        "MOTION_Y_PAPER": 144, # vert motion unit = 1" / MOTION_Y
        "MOTION_X_ROLL" : 180,
        "MOTION_Y_ROLL" : 360,
        "CHAR_WIDTH_H_PAPER": 76/40, # width of a char printed horizontaly
        "CHAR_WIDTH_V_PAPER": 105/50, # width of a char printed verticaly
        "CHAR_WIDTH_H_ROLL" : 71/42,
        "CHAR_WIDTH_V_ROLL" : 84/50,
    },
    "FP-410": {
        # TODO
    }
}
