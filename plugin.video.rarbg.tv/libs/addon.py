# -*- coding: utf-8 -*-
# Module: addon
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
import cPickle as pickle
import xbmcaddon
import xbmc
import xbmcvfs


class Addon(xbmcaddon.Addon):
    """
    Helper class to access addon parameters
    """
    def __init__(self):
        """Class constructor"""
        self._storage = {}
        self._storage_file = None
        self._storage_filename = os.path.join(xbmc.translatePath('special://profile/addon_data').decode('utf-8'),
                                              self.id,
                                              'storage.pcl')
        if not xbmcvfs.exists(self._storage_filename):
            with open(self._storage_filename, 'wb') as file_:
                pickle.dump(self._storage, file_)

    def log(self, message):
        """
        Logger method
        """
        xbmc.log('{0}: {1}'.format(self.id, message))

    def get_storage(self, storage):
        """
        Get named storage object
        :param storage:
        :return: dict
        """
        with open(self._storage_filename, 'rb') as file_:
            pass

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
