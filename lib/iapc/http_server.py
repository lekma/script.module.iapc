# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


__all__ = ["http", "Server"]


import socket

from six import text_type
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from six.moves.urllib.parse import urlparse

from .tools import (
    LOGERROR, log, getAddonId, getAddonVersion, formatException, parseQuery
)


# http -------------------------------------------------------------------------

def http(path=None):
    def decorator(func):
        func.__http__ = path or "/{}".format(func.__name__)
        return func
    return decorator


# ------------------------------------------------------------------------------
# RequestHandler
# ------------------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):

    server_version = "{}/{}".format(getAddonId(), getAddonVersion())

    __fmt_log__ = "httpd: error processing request: [{} - {}]{}"

    def log_error(self, format, *args):
        log(format % args, level=LOGERROR)

    def log_message(self, format, *args):
        log(format % args)

    def end_headers(self):
        self.send_header("X-Clacks-Overhead", "GNU Terry Pratchett")
        BaseHTTPRequestHandler.end_headers(self)

    def send_error(self, code, text=None, headers=None):
        try:
            message, _text_ = self.responses[code]
        except KeyError:
            message, _text_ = "???", "???"
        if text:
            _text_log_ = "\n{}".format(text)
        else:
            _text_log_ = ""
            text = _text_
        log(self.__fmt_log__.format(code, message, _text_log_), level=LOGERROR)
        self.send_response(code, message)
        if headers:
            for header in headers.items():
                self.send_header(*header)
        content = None
        if code >= 200 and code not in (204, 205, 304):
            content = self.send_content_headers(text, "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD" and content:
            self.wfile.write(content)

    # --------------------------------------------------------------------------

    def send_content_headers(self, content, mimeType):
        if isinstance(content, text_type):
            content = content.encode("utf-8")
        self.send_header("Content-Type", "{}; charset=utf-8".format(mimeType))
        self.send_header("Content-Length", str(len(content)))
        return content

    def process_content(self, code, content=None, headers=None):
        self.send_response(code)
        if content:
            content = self.send_content_headers(*content)
        if headers:
            for header in headers.items():
                self.send_header(*header)
        self.end_headers()
        return content

    def _execute(self):
        try:
            return self.server._execute(self)
        except Exception:
            self.send_error(500, text=formatException())

    # --------------------------------------------------------------------------

    def do_HEAD(self):
        self._execute()

    def do_GET(self):
        content = self._execute()
        if content:
            self.wfile.write(content)


# ------------------------------------------------------------------------------
# Server
# ------------------------------------------------------------------------------

class Server(HTTPServer):

    @staticmethod
    def _localhost():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()
        finally:
            s.close()

    @staticmethod
    def _setup(obj):
        for name in dir(obj):
            if not name.startswith("_"):
                method = getattr(obj, name)
                if callable(method):
                    path = getattr(method, "__http__", "")
                    if path and path.startswith("/"):
                        yield path, method

    def __init__(self, timeout=-1):
        self.timeout = None if timeout < 0 else timeout
        self.__methods__ = {}
        self.__methods__.update(self._setup(self))
        HTTPServer.__init__(self, self._localhost(), RequestHandler)
        log("httpd: server started on: {}".format(self.server_address))

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        HTTPServer.server_bind(self)

    def server_close(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        HTTPServer.server_close(self)
        self.__methods__.clear()
        log("httpd: server stopped")

    # --------------------------------------------------------------------------

    def _execute(self, request):
        url = urlparse(request.path)
        try:
            method = self.__methods__[url.path]
        except KeyError:
            request.send_error(404)
        else:
            result = method(**parseQuery(url.query))
            if result:
                return request.process_content(*result)
            request.send_error(500)

