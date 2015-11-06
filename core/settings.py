#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import os
import re
import socket
import stat
import subprocess

from core.attribdict import AttribDict

config = AttribDict()

NAME = "tsusen"
VERSION = "0.3"
DEBUG = False
SNAP_LEN = 100
IPPROTO = 8
ETH_LENGTH = 14
IPPROTO_LUT = dict(((getattr(socket, _), _.replace("IPPROTO_", "")) for _ in dir(socket) if _.startswith("IPPROTO_")))
LOCAL_ADDRESSES = []
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SYSTEM_LOG_DIRECTORY = "/var/log" if not subprocess.mswindows else "C:\\Windows\\Logs"
LOG_DIRECTORY = os.path.join(SYSTEM_LOG_DIRECTORY, NAME)
DEFAULT_LOG_PERMISSIONS = stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH
CSV_HEADER = "proto dst_port dst_ip src_ip first_seen last_seen count"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HTML_DIR = os.path.join(ROOT_DIR, "html")
CONFIG_FILE = os.path.join(ROOT_DIR, "tsusen.conf")
DISABLED_CONTENT_EXTENSIONS = (".py", ".pyc", ".md", ".bak", ".conf", ".zip", "~")
SERVER_HEADER = "%s/%s" % (NAME, VERSION)
MAX_IP_FILTER_RANGE = 2 ** 16

# Reference: https://sixohthree.com/media/2003/06/26/lock_your_doors/portscan.txt
MISC_PORTS = { 17: "qotd", 53: "dns", 135: "dcom-rpc", 502: "modbus", 623: "ipmi", 1433: "mssql", 1723: "pptp", 1900: "upnp", 3128: "squid", 3389: "rdesktop", 5351: "nat-pmp", 5357: "wsdapi", 5631: "pc-anywhere", 5800: "vnc", 5900: "vnc", 5901: "vnc-1", 5902: "vnc-2", 5903: "vnc-3", 6379: "redis", 7547: "cwmp", 8118: "privoxy", 8338: "maltrail", 8339: "tsusen", 8443: "https-alt", 9200: "wap-wsp", 11211: "memcached", 17185: "vxworks", 27017: "mongo", 53413: "netis" }

def read_config(config_file):
    global config

    if not os.path.isfile(config_file):
        exit("[!] missing configuration file '%s'" % config_file)

    config.clear()

    try:
        array = None
        content = open(config_file, "rb").read()

        for line in content.split("\n"):
            line = re.sub(r"#.+", "", line)
            if not line.strip():
                continue

            if line.count(' ') == 0:
                array = line.upper()
                config[array] = []
                continue

            if array and line.startswith(' '):
                config[array].append(line.strip())
                continue
            else:
                array = None
                name, value = line = line.strip().split(' ', 1)
                name = name.upper()
                value = value.strip("'\"")

            if name.startswith("USE_"):
                value = value.lower() in ("1", "true")
            elif value.isdigit():
                value = int(value)
            else:
                for match in re.finditer(r"\$([A-Z0-9_]+)", value):
                    if match.group(1) in globals():
                        value = value.replace(match.group(0), globals()[match.group(1)])
                    else:
                        value = value.replace(match.group(0), os.environ.get(match.group(1), match.group(0)))
                if subprocess.mswindows and "://" not in value:
                    value = value.replace("/", "\\")

            config[name] = value

    except (IOError, OSError):
        pass

    for option in ("MONITOR_INTERFACE",):
        if not option in config:
            exit("[!] missing mandatory option '%s' in configuration file '%s'" % (option, config_file))
