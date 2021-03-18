# -*- coding: utf-8 -*-


__all__ = ["dumpObject", "loadObject", "Persistent", "save"]


from pathlib import Path
from pickle import dump, load

from .addon import __addon_profile__


# pickle -----------------------------------------------------------------------

def dumpObject(obj, path):
    with path.open("wb+") as f:
        dump(obj, f, -1)


def loadObject(path, default=None):
    if path.exists():
        with path.open("rb") as f:
            return load(f)
    return default


# ------------------------------------------------------------------------------
# Persistent

def save(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        finally:
            self.__save__()
    return wrapper


class Persistent(object):

    def __init_subclass__(cls, **kwargs):
        cls.__loading__ = False
        cls.__path__ = Path(
            __addon_profile__,
            getattr(cls, "__pickle__", f"{cls.__name__.lower()}.pickle")
        )
        super().__init_subclass__(**kwargs)

    def __new__(cls, *args, **kwargs):
        if not cls.__path__.exists() or cls.__loading__:
            return super().__new__(cls, *args, **kwargs)
        cls.__loading__ = True
        try:
            with cls.__path__.open("rb") as f:
                return load(f)
        finally:
            cls.__loading__ = False

    def __init__(self, *args, **kwargs):
        if not self.__path__.exists():
            super().__init__(*args, **kwargs)

    def __save__(self):
        with self.__path__.open("wb+") as f:
            dump(self, f, -1)

