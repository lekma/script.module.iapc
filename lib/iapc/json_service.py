# -*- coding: utf-8 -*-





__all__ = ["public", "Service", "Client"]


import json
import uuid

from six import raise_from
from kodi_six import xbmc

from .tools import LOGERROR, log, getAddonId, formatException, JSONRPCError


# public -----------------------------------------------------------------------

def public(func):
    func.__public__ = True
    return func


# ------------------------------------------------------------------------------
# Monitor
# ------------------------------------------------------------------------------

class Monitor(xbmc.Monitor):

    __request__ = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "JSONRPC.NotifyAll"
    }

    def send(self, sender, message, data):
        params = {
            "message": message,
            "sender": sender,
            "data": data
        }
        error = json.loads(
            xbmc.executeJSONRPC(
                json.dumps(dict(self.__request__, params=params)))).get("error")
        if error:
            raise JSONRPCError(error)


# ------------------------------------------------------------------------------
# Service
# ------------------------------------------------------------------------------

class Service(Monitor):

    @staticmethod
    def _setup(value, key=None):
        for name in dir(value):
            if not name.startswith("_"):
                method = getattr(value, name)
                if callable(method) and getattr(method, "__public__", False):
                    name = ".".join((key, name)) if key else name
                    yield name, method

    __request_error_msg__ = "error processing request: [{}]"
    __error_msg__ = "{0.__class__.__name__}: {0}"

    def __init__(self, sender=None):
        self.sender = sender or getAddonId()
        self.__methods__ = {}

    def serve_forever(self, timeout):
        while not self.waitForAbort(timeout):
            pass

    def serve(self, timeout=-1, **kwargs):
        self.__methods__.update(self._setup(self))
        for key, value in list(kwargs.items()):
            self.__methods__.update(self._setup(value, key))
        try:
            self.serve_forever(timeout)
        finally:
            self.__methods__.clear() # clear possible circular references

    def log(self, msg, level=LOGERROR):
        log("service: {}".format(msg), sender=self.sender, level=level)

    def execute(self, request):
        try:
            name, args, kwargs = json.loads(request)
            try:
                method = self.__methods__[name]
            except KeyError:
                raise_from(AttributeError("no method '{0}'".format(name)), None)
            else:
                response = {"result": method(*args, **kwargs)}
        except Exception as error:
            self.log(
                self.__request_error_msg__.format(
                    self.__error_msg__.format(error)
                )
            )
            response = {"error": {"traceback": formatException()}}
        finally:
            return response

    def onNotification(self, sender, method, request):
        if sender == self.sender:
            message = method.split(".", 1)[1]
            self.send(message, sender, self.execute(request))


# ------------------------------------------------------------------------------
# Client
# ------------------------------------------------------------------------------

class RequestError(Exception):

    __unknown_msg__ = "unknown error"

    def __init__(self, error=None):
        super(RequestError, self).__init__(
            error["traceback"].encode("utf-8") if error else self.__unknown_msg__
        )

    def __str__(self):
        return b"remote traceback: {}".format(super(RequestError, self).__str__())


def unpack(response):
    response = json.loads(response)
    try:
        return response["result"]
    except KeyError:
        return RequestError(response["error"])


class Request(Monitor):

    def __init__(self, sender):
        self.sender = sender
        self.message = uuid.uuid4().hex
        self.response = RequestError()
        self.ready = False

    def execute(self, request):
        self.send(self.sender, self.message, request)
        while not self.ready:
            if self.waitForAbort(1):
                break
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    def onNotification(self, sender, method, response):
        if sender == self.message:
            message = method.split(".", 1)[1]
            if message == self.sender:
                self.response = unpack(response)
                self.ready = True


class Attribute(object):

    def __init__(self, sender, name):
        self.sender = sender
        self.name = name

    def __getattr__(self, name):
        return Attribute(self.sender, ".".join((self.name, name)))

    def __call__(self, *args, **kwargs):
        return Request(self.sender).execute((self.name, args, kwargs))


class Client(object):

    def __init__(self, sender=None):
        self.sender = sender or getAddonId()

    def __getattr__(self, name):
        return Attribute(self.sender, name)

