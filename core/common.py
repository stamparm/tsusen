#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import os
import subprocess

def addr_to_int(value):
    _ = value.split('.')
    return (long(_[0]) << 24) + (long(_[1]) << 16) + (long(_[2]) << 8) + long(_[3])

def int_to_addr(value):
    return '.'.join(str(value >> n & 0xFF) for n in (24, 16, 8, 0))

def make_mask(bits):
    return 0xffffffff ^ (1 << 32 - bits) - 1

def check_sudo():
    retval = None

    if not subprocess.mswindows:
        if getattr(os, "geteuid"):
            retval = os.geteuid() == 0
    else:
        import ctypes
        retval = ctypes.windll.shell32.IsUserAnAdmin()

    return retval
