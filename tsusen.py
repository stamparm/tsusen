#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import socket
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

    try:
        start_httpd()
    except socket.error, ex:
        exit("[x] can't start the HTTP server ('%s')" % ex)

    start_sensor()

if __name__ == "__main__":
    main()
