# -*- coding: utf-8 -*-





from sys import exc_info
from traceback import format_exception

from six import u
from six.moves.urllib.parse import parse_qsl
from kodi_six import xbmcaddon, xbmc


# addon infos (modified) -------------------------------------------------------

def getAddonId():
    return xbmcaddon.Addon().getAddonInfo("id")

def getAddonVersion():
    return xbmcaddon.Addon().getAddonInfo("version")


# logging (modified) -----------------------------------------------------------

LOGDEBUG=xbmc.LOGDEBUG
LOGINFO=xbmc.LOGINFO
LOGWARNING=xbmc.LOGWARNING
LOGERROR=xbmc.LOGERROR

def log(message, sender=None, level=LOGINFO):
    xbmc.log("[{}] {}".format(sender or getAddonId(), message), level=level)


# encode exception -------------------------------------------------------------

def formatException(limit=None):
    try:
        etype, value, tb = exc_info()
        lines = format_exception(etype, value, tb, limit)
        lines, line = lines[:-1], lines[-1]
        lines.append(u(line).encode("utf-8"))
        return "".join(line.decode("utf-8") for line in lines)
    finally:
        etype = value = tb = None


# parseQuery -------------------------------------------------------------------

__parse_consts__ = {
    "none": None,
    "true": True,
    "false": False
}

def parseValue(value):
    try:
        return __parse_consts__[value.lower()]
    except KeyError:
        return value

def parseQuery(query):
    if query.startswith("?"):
        query = query[1:]
    return {k: parseValue(v) for k, v in parse_qsl(query)}


# JSONRPCError -----------------------------------------------------------------

class JSONRPCError(Exception):

    __error_msg__ = "[{code}] {message}"
    __data_msg__ = "in {method}."
    __stack_msg__ = "{message} ({name})"

    def __init__(self, error):
        message = self.__error_msg__.format(**error)
        data = error.get("data")
        if data:
            message = " ".join((message, self.data(data)))
        super(JSONRPCError, self).__init__(message)

    def data(self, data):
        message = self.__data_msg__.format(**data)
        try:
            # unfortunately kodi doesn't respect its own specification :(
            try:
                _message_ = data["message"]
            except KeyError:
                _message_ = self.stack(data["stack"])
            message = " ".join((_message_, message))
        except KeyError:
            pass
        return message

    def stack(self, stack):
        return self.__stack_msg__.format(**stack)
