# -*- coding: utf-8 -*-
# Module: views
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xbmcplugin
import xbmcgui


def root_view(plugin_url, plugin_handle):
    """
    Plugin root view
    :return:
    """
    episodes_item = xbmcgui.ListItem(label='[TV Episodes]')
    url = '{0}?acton=episode_list'.format(plugin_url)
    xbmcplugin.addDirectoryItem(plugin_handle, url, episodes_item, isFolder=True)
    xbmcplugin.endOfDirectory(plugin_handle, True)


def episode_list_view(plugin_url, plugin_handle):
    """
    The list of episode receases by most recent first
    :param plugin_url:
    :param plugin_handle:
    :return:
    """
    xbmcplugin.endOfDirectory(plugin_handle, True)
