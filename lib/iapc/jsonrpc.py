# -*- coding: utf-8 -*-


from json import dumps, loads

import xbmc


# ------------------------------------------------------------------------------
# JSONRPC

class JSONRPCError(Exception):

    def __init__(self, error):
        message = f"[{error['code']}] {error['message']}".rstrip(".")
        if (data := error.get("data")):
            message = f"{message} {self.__data__(data)}"
        super().__init__(message)

    def __data__(self, data):
        message = f"in {data['method']}"
        if (stack := data.get("stack")):
            message = f"{message} {self.__stack__(stack)}"
        return message

    def __stack__(self, stack):
        return f"({stack['message']} ('{stack['name']}'))"


def executeJSONRPC(method, **params):
    request = {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}
    if (error := loads(xbmc.executeJSONRPC(dumps(request))).get("error")):
        raise JSONRPCError(error)


# ------------------------------------------------------------------------------
# Monitor

class Monitor(xbmc.Monitor):

    @staticmethod
    def send(sender, message, data):
        executeJSONRPC(
            "JSONRPC.NotifyAll", sender=sender, message=message, data=data
        )

