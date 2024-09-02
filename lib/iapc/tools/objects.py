# -*- coding: utf-8 -*-


__all__ = ["Type", "Object", "List"]


# ------------------------------------------------------------------------------
# Type

def __property__(name, func):
    def getter(obj):
        return func(obj.__getattr__(name))
    return property(getter)


class Type(type):

    __transform__ = {}

    def __new__(cls, name, bases, namespace, **kwargs):
        namespace.setdefault("__slots__", set())
        namespace.setdefault(
            "__getattr_error__", f"'{name}' object has no attribute '{{}}'"
        )
        for _name_, _func_ in namespace.pop("__transform__", dict()).items():
            namespace[_name_] = __property__(_name_, _func_)
        for _type_, _func_ in cls.__transform__.items():
            for _name_ in namespace.pop(_type_, set()):
                namespace[_name_] = __property__(_name_, _func_)
        return super(Type, cls).__new__(cls, name, bases, namespace, **kwargs)


# ------------------------------------------------------------------------------
# Object

class Object(object, metaclass=Type):

    __slots__ = {"__data__"}

    def __new__(cls, data, **kwargs):
        if isinstance(data, dict):
            if not data:
                return None
            return super(Object, cls).__new__(cls)
        return data

    def __init__(self, data, **kwargs):
        self.__data__ = dict(
            data, kwargs=dict(data.get("kwargs", {}), **kwargs)
        )
        #self.__data__ = data
        #self.__data__.setdefault("kwargs", {}).update(**kwargs)

    def __getitem__(self, name):
        return self.__data__[name]

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(self.__getattr_error__.format(name)) from None

    def get(self, *args):
        return self.__data__.get(*args)

    def getItem(self, *args, **kwargs):
        raise NotImplementedError


# ------------------------------------------------------------------------------
# List

class List(list):

    __ctor__ = Object

    def __init__(self, items, category=None, content=None, **kwargs):
        if self.__ctor__:
            items = (self.__ctor__(item, **kwargs) for item in items)
        super(List, self).__init__(items)
        self.category = category
        self.content = content

    def getItems(self, *args, **kwargs):
        return (item.getItem(*args, **kwargs) for item in self if item)

