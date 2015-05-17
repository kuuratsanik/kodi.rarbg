# -*- coding: utf-8 -*-
# Module: addon
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
from datetime import datetime, timedelta
from cPickle import load, dump, PickleError
import xbmcaddon
import xbmc


class _Storage(object):
    """Persistent storage"""
    def __init__(self, path):
        self._storage = {}
        filename = os.path.join(path, 'storage.pcl')
        if os.path.exists(filename):
            mode = 'r+b'
        else:
            mode = 'w+b'
        self._file = open(filename, mode)
        try:
            self._storage = load(self._file)
        except (PickleError, EOFError):
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.flush()

    def __getitem__(self, key):
        return self._storage[key]

    def __setitem__(self, key, value):
        self._storage[key] = value

    def flush(self):
        """
        Flush storage to disk
        :return:
        """
        self._file.seek(0)
        dump(self._file, self._storage)
        self._file.truncate()
        self._file.close()


class Addon(xbmcaddon.Addon):
    """
    Helper class to access addon parameters
    """
    def log(self, message):
        """
        Logger method
        """
        xbmc.log('{0}: {1}'.format(self.id, message))

    @property
    def id(self):
        """
        Addon ID as a string
        :return: str
        """
        return self.getAddonInfo('id')

    @property
    def path(self):
        """
        Addon folder
        :return:
        """
        return self.getAddonInfo('path').decode('utf-8')

    def get_storage(self):
        """
        Get a storage object
        :return:
        """
        return _Storage(xbmc.translatePath('special://profile/addon_data/{0}'.format(self.id)).decode('utf-8'))


def cached(duration=10):
    """
    Cache decorator
    duration - cache time in min
    :param duration: int
    :return:
    """
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            addon = Addon()
            with addon.get_storage() as storage:
                try:
                    storage['cache']
                except KeyError:
                    storage['cache'] = {}
                current_time = datetime.now()
                key = str(args) + str(kwargs)
                try:
                    page, timestamp = storage['cache'][key]
                    if current_time - timestamp > timedelta(minutes=duration):
                        raise KeyError
                except KeyError:
                    page = func(*args, **kwargs)
                    storage['cache'][key] = (page, current_time)
            return page
        return inner_wrapper
    return outer_wrapper
