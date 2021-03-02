# -*- coding: utf-8 -*-


__all__ = ["http", "Server"]


from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from traceback import format_exc
from urllib.parse import urlparse

from .tools import Logger, getAddonVersion, parseQuery


# http -------------------------------------------------------------------------

def http(path=None):
    def decorator(func):
        func.__http__ = path or f"/{func.__name__}"
        return func
    return decorator


# ------------------------------------------------------------------------------
# RequestHandler

class RequestHandler(BaseHTTPRequestHandler):

    def log_error(self, format, *args):
        self.server.logger.error(format % args)

    def log_message(self, format, *args):
        self.server.logger.info(format % args)

    def end_headers(self):
        self.send_header("X-Clacks-Overhead", "GNU Terry Pratchett")
        super().end_headers()

    def send_response(self, code, message=None, explain=None):
        if isinstance(code, HTTPStatus):
            code = code.value
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = "???", "???"
        if message is None:
            message = shortmsg
        log = f"'{self.requestline}' => ({code} - {message})"
        if explain:
            log = f"{log}\n{explain}"
        else:
            explain = longmsg
        if code >= 400:
            self.server.logger.error(log)
        else:
            self.server.logger.info(log)
        self.send_response_only(code, message)
        self.send_header("Server", self.version_string())
        self.send_header("Date", self.date_time_string())
        return explain

    def send_error(self, code, message=None, explain=None):
        explain = self.send_response(code, message, explain)
        content = None
        if code >= 200 and code not in (204, 205, 304):
            content = self.send_content_headers(explain, "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD" and content:
            self.wfile.write(content)

    # --------------------------------------------------------------------------

    def send_content_headers(self, content, mimeType):
        if isinstance(content, str):
            content = content.encode("utf-8")
        self.send_header("Content-Type", f"{mimeType}; charset=utf-8")
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

    def execute(self):
        try:
            return self.server.execute(self)
        except Exception:
            self.send_error(500, explain=format_exc().strip())

    # --------------------------------------------------------------------------

    def do_HEAD(self):
        self.execute()

    def do_GET(self):
        if (content := self.execute()):
            self.wfile.write(content)


# ------------------------------------------------------------------------------
# Server

class Server(HTTPServer):

    @staticmethod
    def __localhost__():
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()

    @staticmethod
    def __methods__(obj):
        for name in dir(obj):
            if (
                (not name.startswith("_")) and
                (callable(method := getattr(obj, name))) and
                ((path := getattr(method, "__http__", "")).startswith("/"))
            ):
                yield path, method

    def __init__(self, id, timeout=-1):
        self.logger = Logger(id, component="httpd")
        self.timeout = None if timeout < 0 else timeout
        self.methods = {k: v for k, v in self.__methods__(self)}
        RequestHandler.server_version = f"{id}/{getAddonVersion()}"
        super().__init__(self.__localhost__(), RequestHandler)
        self.logger.info(f"started on: {self.server_address}")

    def server_close(self):
        self.socket.shutdown(SHUT_RDWR)
        super().server_close()
        self.methods.clear()
        self.logger.info("stopped")

    def execute(self, request):
        url = urlparse(request.path)
        try:
            method = self.methods[url.path]
        except KeyError:
            request.send_error(404)
        else:
            result = method(**parseQuery(url.query))
            if result:
                return request.process_content(*result)
            request.send_error(500)

