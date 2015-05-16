# -*- coding: utf-8 -*-
# Module: addon
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xbmcaddon
import xbmc


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
