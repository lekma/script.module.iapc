# -*- coding: utf-8 -*-


from urllib.parse import parse_qsl

import xbmc, xbmcaddon


# addon infos (modified) -------------------------------------------------------

def getAddonId():
    return xbmcaddon.Addon().getAddonInfo("id")

def getAddonVersion():
    return xbmcaddon.Addon().getAddonInfo("version")


# logging (modified) -----------------------------------------------------------

class Logger(object):

    DEBUG=xbmc.LOGDEBUG
    INFO=xbmc.LOGINFO
    WARNING=xbmc.LOGWARNING
    ERROR=xbmc.LOGERROR

    def __init__(self, id, component=""):
        self.id = id
        self.component = component
        self.__prefix__ = (
            f"{f'[{self.id}] ' if self.id else ''}"
            f"{f'{self.component}: ' if self.component else ''}"
        )

    def __log__(self, message, level):
        xbmc.log(f"{self.__prefix__}{message}", level=level)

    def debug(self, message):
        self.__log__(message, self.DEBUG)

    def info(self, message):
        self.__log__(message, self.INFO)

    def warning(self, message):
        self.__log__(message, self.WARNING)

    def error(self, message):
        self.__log__(message, self.ERROR)

    def getLogger(self, component=""):
        if component == self.component:
            return self
        return Logger(self.id, component=component)


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
    return {
        k: parseValue(v)
        for k, v in parse_qsl(query[1:] if query.startswith("?") else query)
    }

