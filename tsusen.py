#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import sys

sys.dont_write_bytecode = True

from core.monitor import init
from core.monitor import start

def main():
    """
    Main function
    """

    init()
    start()

if __name__ == "__main__":
    main()
