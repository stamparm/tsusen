#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import sys

sys.dont_write_bytecode = True

from core.sensor import init_sensor
from core.sensor import start_sensor
from core.httpd import start_httpd

def main():
    """
    Main function
    """

    init_sensor()
    start_httpd()
    start_sensor()

if __name__ == "__main__":
    main()
