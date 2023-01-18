# -*- coding: utf-8 -*-


__all__ = [
    "getWindowId", "ICONINFO", "ICONWARNING", "ICONERROR", "notify",
    "selectDialog", "inputDialog", "contextMenu", "browseDialog", "browseFiles",
    "ListItem"
]


import xbmc, xbmcgui

from .addon import getAddonName, getAddonIcon, maybeLocalize


# getWindowId ------------------------------------------------------------------

def getWindowId():
    return xbmcgui.getCurrentWindowId()


# notify -----------------------------------------------------------------------

ICONINFO = xbmcgui.NOTIFICATION_INFO
ICONWARNING = xbmcgui.NOTIFICATION_WARNING
ICONERROR = xbmcgui.NOTIFICATION_ERROR

def notify(message, heading=getAddonName(), icon=getAddonIcon(), time=5000):
    xbmcgui.Dialog().notification(
        maybeLocalize(heading), maybeLocalize(message), icon=icon, time=time
    )


# select -----------------------------------------------------------------------

def selectDialog(_list_, heading=getAddonName(), multi=False, **kwargs):
    if multi:
        return xbmcgui.Dialog().multiselect(
            maybeLocalize(heading), _list_, **kwargs
        )
    return xbmcgui.Dialog().select(maybeLocalize(heading), _list_, **kwargs)


# input ------------------------------------------------------------------------

def inputDialog(heading=getAddonName(), **kwargs):
    return xbmcgui.Dialog().input(maybeLocalize(heading), **kwargs)


# contextmenu ------------------------------------------------------------------

def contextMenu(_list_):
    return xbmcgui.Dialog().contextmenu(_list_)


# browse -----------------------------------------------------------------------

def browseDialog(_type_, heading=getAddonName(), source="", multi=False, **kwargs):
    return xbmcgui.Dialog().browse(
        _type_, maybeLocalize(heading), source, enableMultiple=multi, **kwargs
    )

def browseFiles(**kwargs):
    return browseDialog(1, **kwargs)


# listitem ---------------------------------------------------------------------

class ListItem(xbmcgui.ListItem):

    def __new__(cls, label, path, **kwargs):
        return super(ListItem, cls).__new__(cls, label=label, path=path)

    def __init__(
        self, label, path, isFolder=False, isPlayable=True,
        infoLabels=None, streamInfos=None, contextMenus=None, **art
    ):
        super(ListItem, self).__init__(label=label, path=path)
        self.setIsFolder(isFolder)
        self.setIsPlayable(False if isFolder else isPlayable)
        if infoLabels:
            self.setInfoLabels(infoLabels)
        if streamInfos:
            self.addStreamInfos(streamInfos)
        if contextMenus:
            self.addContextMenuItems(contextMenus)
        if art:
            self.setArt(art)

    def setIsFolder(self, isFolder):
        super(ListItem, self).setIsFolder(isFolder)
        #self.setProperty("IsFolder", str(isFolder).lower())
        self.isFolder = isFolder

    def setIsPlayable(self, isPlayable):
        self.setProperty("IsPlayable", str(isPlayable).lower())
        self.isPlayable = isPlayable

    def asItem(self):
        return (self.getPath(), self, self.isFolder)

    # getInfoTag ---------------------------------------------------------------

    __info_tags__ = {
        "video": "getVideoInfoTag",
        "music": "getMusicInfoTag",
        "game": "getGameInfoTag"
    }

    def getInfoTag(self, _type_):
        return getattr(self, self.__info_tags__[_type_])()

    # addStreamInfos -----------------------------------------------------------

    __stream_infos__ = {
        "video": ("addVideoStream", xbmc.VideoStreamDetail),
        "audio": ("addAudioStream", xbmc.AudioStreamDetail),
        "subtitle": ("addSubtitleStream", xbmc.SubtitleStreamDetail)
    }

    def addStreamInfos(self, streamInfos):
        infoTag = self.getInfoTag("video")
        for _type_, infos in streamInfos.items():
            method, _class_ = self.__stream_infos__[_type_]
            getattr(infoTag, method)(_class_(**infos))

    # setInfoLabels ------------------------------------------------------------

    __info_labels__ = {
        "video": {
            "aired": "setFirstAired",
            "album": "setAlbum",
            "artist": "setArtists",
            "cast": "setCast",
            "castandrole": "setCast",
            "code": "setProductionCode",
            "country": "setCountries",
            "credits": "setWriters",
            "dateadded": "setDateAdded",
            "dbid": "setDbId",
            "director": "setDirectors",
            "duration": "setDuration",
            "episode": "setEpisode",
            "episodeguide": "setEpisodeGuide",
            "filenameandpath": "setFilenameAndPath",
            "genre": "setGenres",
            "imdbnumber": "setIMDBNumber",
            "lastplayed": "setLastPlayed",
            "mediatype": "setMediaType",
            "mpaa": "setMpaa",
            "originaltitle": "setOriginalTitle",
            "path": "setPath",
            "playcount": "setPlaycount",
            "plot": "setPlot",
            "plotoutline": "setPlotOutline",
            "premiered": "setPremiered",
            "rating": "setRatings",
            "resumepoint": "setResumePoint",
            "season": "setSeason",
            "set": "setSet",
            "setid": "setSetId",
            "setoverview": "setSetOverview",
            "showlink": "setShowLinks",
            "sortepisode": "setSortEpisode",
            "sortseason": "setSortSeason",
            "sorttitle": "setSortTitle",
            "status": "setTvShowStatus",
            "studio": "setStudios",
            "tag": "setTags",
            "tagline": "setTagLine",
            "title": "setTitle",
            "top250": "setTop250",
            "tracknumber": "setTrackNumber",
            "trailer": "setTrailer",
            "tvshowtitle": "setTvShowTitle",
            "uniqueids": "setUniqueIDs",
            "userrating": "setUserRating",
            "votes": "setVotes",
            "writer": "setWriters",
            "year": "setYear"
        },
        "music": {
            "album": "setAlbum",
            "albumartist": "setAlbumArtist",
            "artist": "setArtist",
            "comment": "setComment",
            "dbid": "setDbId",
            "discnumber": "setDisc",
            "duration": "setDuration",
            "genre": "setGenres",
            "lastplayed": "setLastPlayed",
            "listeners": "setListeners",
            "lyrics": "setLyrics",
            "mediatype": "setMediaType",
            "musicbrainzalbumartistid": "setMusicBrainzAlbumArtistID",
            "musicbrainzalbumid": "setMusicBrainzAlbumID",
            "musicbrainzartistid": "setMusicBrainzArtistID",
            "musicbrainzreleasegroupid": "setMusicBrainzReleaseGroupID",
            "musicbrainztrackid": "setMusicBrainzTrackID",
            "playcount": "setPlayCount",
            "rating": "setRating",
            "releasedate": "setReleaseDate",
            "title": "setTitle",
            "tracknumber": "setTrack",
            "url": "setURL",
            "userrating": "setUserRating",
            "year": "setYear"
        },
        "game": {
            "developer": "setDeveloper",
            "gameclient": "setGameClient",
            "genres": "setGenres",
            "overview": "setOverview",
            "platform": "setPlatform",
            "publisher": "setPublisher",
            "title": "setTitle",
            "year": "setYear"
        }
    }

    def setInfoLabels(self, infoLabels):
        for _type_, labels in infoLabels.items():
            infoTag = self.getInfoTag(_type_)
            methods = self.__info_labels__[_type_]
            for label, value in labels.items():
                getattr(infoTag, methods[label])(value)
