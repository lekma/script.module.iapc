# -*- coding: utf-8 -*-


from urllib.parse import parse_qsl

import xbmc, xbmcaddon


# addon infos (modified) -------------------------------------------------------

def getAddonId():
    return xbmcaddon.Addon().getAddonInfo("id")

def getAddonVersion():
    return xbmcaddon.Addon().getAddonInfo("version")


# logging (modified) -----------------------------------------------------------

def log(message, level=xbmc.LOGINFO):
    xbmc.log(message, level=level)


class Logger(object):

    def __init__(self, id, component=""):
        self.id = id
        self.component = component
        self.__prefix__ = (
            f"{f'[{self.id}] ' if self.id else ''}"
            f"{f'{self.component}: ' if self.component else ''}"
        )

    def __log__(self, message, level):
        log(f"{self.__prefix__}{message}", level=level)

    def debug(self, message):
        self.__log__(message, xbmc.LOGDEBUG)

    def info(self, message):
        self.__log__(message, xbmc.LOGINFO)

    def warning(self, message):
        self.__log__(message, xbmc.LOGWARNING)

    def error(self, message):
        self.__log__(message, xbmc.LOGERROR)

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
    if query.startswith("?"):
        query = query[1:]
    return {k: parseValue(v) for k, v in parse_qsl(query)}

