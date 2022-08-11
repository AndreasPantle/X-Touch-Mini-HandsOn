# -*- coding: utf-8 -*-


# Creates a string from a bytearray for printing
bytes_to_hex_str = lambda b: ' '.join('0x%02x' % i for i in b)
