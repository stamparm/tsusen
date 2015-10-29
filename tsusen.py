#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import sys

sys.dont_write_bytecode = True

from core.common import init
from core.common import monitor

def main():
    """
    Main function
    """

    init()
    monitor()

if __name__ == "__main__":
    main()
