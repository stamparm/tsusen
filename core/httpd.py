import BaseHTTPServer
import cStringIO
import httplib
import mimetypes
import gzip
import os
import SocketServer
import threading
import traceback
import urlparse

from settings import DISABLED_CONTENT_EXTENSIONS
from settings import DEBUG
from settings import SERVER_HEADER
from settings import HTML_DIR
from settings import HTTP_ADDRESS
from settings import HTTP_PORT

class ThreadingServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def finish_request(self, *args, **kwargs):
        try:
            BaseHTTPServer.HTTPServer.finish_request(self, *args, **kwargs)
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
            content = self._format(open(path, "rb").read(), URL=self.path)
            self.send_response(httplib.NOT_FOUND)
            self.send_header("Connection", "close")

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
        except:
            if DEBUG:
                traceback.print_exc()

def start_httpd():
    server = ThreadingServer((HTTP_ADDRESS, HTTP_PORT), ReqHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
