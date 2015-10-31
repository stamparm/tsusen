#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import BaseHTTPServer
import csv
import cStringIO
import httplib
import mimetypes
import glob
import gzip
import os
import re
import socket
import SocketServer
import threading
import traceback
import urlparse

from settings import config
from settings import DEFAULT_LOG_PERMISSIONS
from settings import DISABLED_CONTENT_EXTENSIONS
from settings import DEBUG
from settings import SERVER_HEADER
from settings import HTML_DIR
from settings import LOG_DIRECTORY
from settings import MISC_PORTS

class ThreadingServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def finish_request(self, *args, **kwargs):
        try:
            BaseHTTPServer.HTTPServer.finish_request(self, *args, **kwargs)
        except KeyboardInterrupt:
            raise
        except:
            if DEBUG:
                traceback.print_exc()

class ReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        path, query = self.path.split('?', 1) if '?' in self.path else (self.path, "")
        params = {}
        content = None

        if hasattr(self, "data"):
            params.update(urlparse.parse_qs(self.data))

        if query:
            params.update(urlparse.parse_qs(query))

        for key in params:
            if params[key]:
                params[key] = params[key][-1]

        if path == '/':
            path = "index.html"

        path = path.strip('/')

        path = path.replace('/', os.path.sep)
        path = os.path.abspath(os.path.join(HTML_DIR, path)).strip()

        if ".." not in os.path.relpath(path, HTML_DIR) and os.path.isfile(path) and not path.endswith(DISABLED_CONTENT_EXTENSIONS):
            content = open(path, "rb").read()
            self.send_response(httplib.OK)
            self.send_header("Connection", "close")
            self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")

        else:
            path = os.path.abspath(os.path.join(HTML_DIR, "404.html")).strip()
            content = open(path, "rb").read()
            self.send_response(httplib.NOT_FOUND)
            self.send_header("Connection", "close")

        for match in re.finditer(r"<\!(\w+)\!>", content):
            name = match.group(1)
            _ = getattr(self, "_%s" % name.lower(), None)
            if _:
                content = self._format(content, **{ name: _() })

        if content is not None:
            length = len(content)

            if "gzip" in self.headers.getheader("Accept-Encoding", ""):
                self.send_header("Content-Encoding", "gzip")
                self.send_header("Transfer-Encoding", "chunked")
                _ = cStringIO.StringIO()
                compress = gzip.GzipFile("", "w+b", 9, _)
                compress._stream = _
                compress.write(content)
                compress.flush()
                compress.close()
                content = compress._stream.getvalue()
            else:
                self.send_header("Content-Length", str(length))

            self.end_headers()
            self.wfile.write(content)
            self.wfile.flush()
            self.wfile.close()

    def do_PUT(self):
        """
        e.g.: curl -T 2015-10-28.csv http://<server>:8339
        """

        path, query = self.path.split('?', 1) if '?' in self.path else (self.path, "")

        path = path.strip('/')
        match = re.search(r"\A([\d-]+)\.csv\Z", path)

        if match:
            date = match.group(1)
        else:
            return

        filename = os.path.join(LOG_DIRECTORY, path)
        length = int(self.headers.getheader('Content-length'))
        content = self.rfile.read(length)

        if not os.path.exists(filename):
            with open(filename, "w+b") as f:
                f.write(content)
            os.chmod(filename, DEFAULT_LOG_PERMISSIONS)
        else:
            first = None
            result = set()

            with open(filename, "r") as f:
                for line in f.xreadlines():
                    line = line.strip()
                    if not line:
                        continue
                    if not first:
                        first = line
                        continue
                    result.add(line)

            for line in content.split("\n")[1:]:
                line = line.strip()
                if not line:
                    continue
                result.add(line)

            with open(filename, "w+b") as f:
                f.write("%s\n" % first)
                for line in result:
                    f.write("%s\n" % line)

        self.send_response(httplib.OK)
        self.send_header("Connection", "close")

    def _url(self):
        return self.path

    def _trendline_data(self):
        result = ""
        series = {}
        dates = set()

        for filename in sorted(glob.glob(os.path.join(LOG_DIRECTORY, "*.csv")))[-config.TRENDLINE_PERIOD:]:
            with open(filename, "rb") as f:
                match = re.search(r"([\d-]+)\.csv", filename)

                if match:
                    date = match.group(1)
                else:
                    continue

                reader = csv.DictReader(f, delimiter=' ')

                for row in reader:
                    try:
                        port = int(row['dst_port'])
                        port_name = MISC_PORTS.get(port) or socket.getservbyport(port, row['proto'].lower())
                    except KeyboardInterrupt:
                        raise
                    except:
                        port_name = None
                    finally:
                        serie = "%s%s%s" % (row['proto'].upper(), " %s" % row['dst_port'] if row['dst_port'].isdigit() else "", " (%s)" % port_name if port_name else "")

                    if serie not in series:
                        series[serie] = {}

                    if date not in series[serie]:
                        series[serie][date] = 0

                    series[serie][date] += 1
                    dates.add(date)

        keys = series.keys()

        if keys:
            last_date = max(dates)
            totals = {}
            for key in list(keys):
                if any(series[key].get(date, 0) < config.TRENDLINE_DAILY_THRESHOLD for date in dates if date != last_date):
                    if all(series[key].get(date, 0) < config.TRENDLINE_DAILY_BURST for date in dates):
                        del keys[keys.index(key)]
                totals[key] = series[key].get(last_date, 0)

            keys = sorted(keys, key=lambda key: totals[key], reverse=True)
            result += "['Date',%s],\n" % ','.join("'%s'" % key for key in keys)

            for date in sorted(dates):
                year, month, day = date.split('-')
                result += "[new Date(%s,%d,%s)," % (year, int(month) - 1, day)
                for serie in keys:
                    result += "%s," % series[serie].get(date, 0)
                result += "],\n"

        return result

    def _format(self, content, **params):
        if content:
            for key, value in params.items():
                content = content.replace("<!%s!>" % key, value)

        return content

    def version_string(self):
        return SERVER_HEADER

    def log_message(self, format, *args):
        return

    def finish(self):
        try:
            BaseHTTPServer.BaseHTTPRequestHandler.finish(self)
        except KeyboardInterrupt:
            raise
        except:
            if DEBUG:
                traceback.print_exc()

def start_httpd():
    server = ThreadingServer((config.HTTP_ADDRESS, config.HTTP_PORT), ReqHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    print "[i] running HTTP server at '%s:%d'" % (config.HTTP_ADDRESS, config.HTTP_PORT)
