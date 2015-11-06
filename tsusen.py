#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import optparse
import socket
import sys

sys.dont_write_bytecode = True

from core.common import check_sudo
from core.sensor import init_sensor
from core.sensor import start_sensor
from core.settings import CONFIG_FILE
from core.settings import NAME
from core.settings import VERSION
from core.settings import read_config
from core.httpd import start_httpd

def main():
    """
    Main function
    """

    print "%s #v%s\n" % (NAME, VERSION)

    if not check_sudo():
        exit("[x] please run with sudo/Administrator privileges")

    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-c", dest="config_file", help="Configuration file (default: tsusen.conf)")
    options, _ = parser.parse_args()

    read_config(options.config_file or CONFIG_FILE)
    init_sensor()

    try:
        start_httpd()
    except socket.error, ex:
        exit("[x] can't start the HTTP server ('%s')" % ex)

    start_sensor()

if __name__ == "__main__":
    main()
