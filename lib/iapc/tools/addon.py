# -*- coding: utf-8 -*-


__all__ = [
    "getAddonId", "getAddonName", "getAddonVersion",
    "getAddonPath", "getAddonIcon", "getAddonProfile",
    "getLanguage", "localizedString", "maybeLocalize",
    "getMediaPath", "getMedia", "makeProfile",
    "openSettings", "getSetting", "setSetting",
    "Logger"
]


from os.path import join

import xbmc, xbmcaddon, xbmcvfs


# addon infos ------------------------------------------------------------------

def getAddonId():
    return xbmcaddon.Addon().getAddonInfo("id")

def getAddonName():
    return xbmcaddon.Addon().getAddonInfo("name")

def getAddonVersion():
    return xbmcaddon.Addon().getAddonInfo("version")

def getAddonPath():
    return xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("path"))

def getAddonIcon():
    return xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("icon"))

def getAddonProfile():
    return xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))


# misc utils -------------------------------------------------------------------

def getLanguage():
    return xbmc.getLanguage(xbmc.ISO_639_1) or "en"


def localizedString(id):
    if id < 30000:
        return xbmc.getLocalizedString(id)
    return xbmcaddon.Addon().getLocalizedString(id)


def maybeLocalize(value):
    if isinstance(value, int):
        return localizedString(value)
    return value


__media_path__ = join(getAddonPath(), "resources", "media")

def getMediaPath(*args):
    return join(__media_path__, *args)


def getMedia(name, ext="png"):
    return getMediaPath(f"{name}.{ext}")


def makeProfile():
    if not xbmcvfs.exists(profile := getAddonProfile()):
        xbmcvfs.mkdirs(profile)


# settings ---------------------------------------------------------------------

def openSettings():
    xbmcaddon.Addon().openSettings()


__get_settings__ = {
    bool: "getSettingBool",
    int: "getSettingInt",
    float: "getSettingNumber",
    str: "getSettingString"
}

def getSetting(id, _type_=None):
    if _type_ is not None:
        return getattr(xbmcaddon.Addon(), __get_settings__[_type_])(id)
    return xbmcaddon.Addon().getSetting(id)


__set_settings__ = {
    bool: "setSettingBool",
    int: "setSettingInt",
    float: "setSettingNumber",
    str: "setSettingString"
}

def setSetting(id, value, _type_=None):
    if _type_ is not None:
        return getattr(xbmcaddon.Addon(), __set_settings__[_type_])(id, value)
    return xbmcaddon.Addon().setSetting(id, value)


# ------------------------------------------------------------------------------
# Logger

class Logger(object):

    DEBUG=xbmc.LOGDEBUG
    INFO=xbmc.LOGINFO
    WARNING=xbmc.LOGWARNING
    ERROR=xbmc.LOGERROR

    def __init__(self, id=None, component=""):
        self.id = id or getAddonId()
        self.component = component
        self.__prefix__ = (
            f"{f'[{self.id}] ' if self.id else ''}"
            f"{f'<{self.component}> ' if self.component else ''}"
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

