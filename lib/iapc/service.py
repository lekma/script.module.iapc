# -*- coding: utf-8 -*-


__all__ = ["public", "Service"]


from json import loads
from traceback import format_exc

import xbmc

from nuttig import executeJSONRPC, getAddonId, Logger


# ------------------------------------------------------------------------------
# Monitor

class Monitor(xbmc.Monitor):

    @staticmethod
    def send(sender, message, data):
        executeJSONRPC(
            "JSONRPC.NotifyAll", sender=sender, message=message, data=data
        )


# public -----------------------------------------------------------------------

def public(func):
    func.__public__ = True
    return func


# ------------------------------------------------------------------------------
# Service

class Service(Monitor):

    @staticmethod
    def __methods__(value, key=None):
        for name in dir(value):
            if (
                (not name.startswith("_")) and
                (callable(method := getattr(value, name))) and
                (getattr(method, "__public__", False))
            ):
                yield f"{key}.{name}" if key else name, method

    def __init__(self):
        self.id = getAddonId()
        self.logger = Logger(self.id, component="service")
        self.methods = {}

    def serve_forever(self, timeout):
        while not self.waitForAbort(timeout):
            pass

    def serve(self, timeout=-1, **kwargs):
        self.methods.update(self.__methods__(self))
        for key, value in kwargs.items():
            self.methods.update(self.__methods__(value, key))
        try:
            self.serve_forever(timeout)
        finally:
            self.methods.clear() # clear possible circular references

    def execute(self, request):
        try:
            name, args, kwargs = loads(request)
            try:
                method = self.methods[name]
            except KeyError:
                raise AttributeError(f"no method '{name}'") from None
            return {"result": method(*args, **kwargs)}
        except Exception:
            error = format_exc().strip()
            self.logger.error(f"error processing request\n{error}")
            return {"error": error}

    def onNotification(self, sender, method, data):
        if sender == self.id:
            self.send(method.split(".", 1)[1], sender, self.execute(data))
