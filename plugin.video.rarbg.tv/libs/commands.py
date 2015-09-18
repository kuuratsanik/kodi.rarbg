# -*- coding: utf-8 -*-
# Module: commands
# Author: Roman V.M.
# Created on: 19.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

"""Commands called via context menu"""

import sys
import os
from urllib import quote
#
import xbmcgui
import xbmc
import xbmcvfs
from simpleplugin import Storage

_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon.png')
_config_dir = xbmc.translatePath('special://profile/addon_data/plugin.video.rarbg.tv/').decode('utf-8')

def add_to_favorites(config_dir, tvdb):
    """
    Add a TV Show to favorites

    @param config_dir: str - Addon config folder
    @param title: str - TV show title
    @param tvdb: str - TheTVDB ID
    @param thumb: str - item's thumbnail image
    @return:
    """
    with Storage(config_dir, 'myshows.pcl') as storage:
        mshows = storage.get('myshows', [])
        if tvdb not in mshows:
            mshows.append(tvdb)
            storage['myshows'] = mshows
            xbmcgui.Dialog().notification('Rarbg', 'The show successfully added to "My Shows"', _icon, 3000)
        else:
            xbmcgui.Dialog().notification('Rarbg', 'The show is already in "My Shows"!', 'error', 3000)


def remove_from_favorites(config_dir, index):
    """
    Remove a TV show from "My Shows"

    @param config_dir: str - Addon config folder
    @param index: str - digital index of the item to be removed
    @return:
    """
    with Storage(config_dir, 'myshows.pcl') as storage:
        del storage['myshows'][int(index)]
    xbmcgui.Dialog().notification('Rarbg', 'The show removed from "My Shows"', _icon, 3000)
    xbmc.executebuiltin('Container.Refresh')


def create_strm(filename, torrent, poster, title, season, episode):
    """
    Create a .strm file for torrent

    @param filename:
    @param torrent:
    @return:
    """
    # todo: finish this
    pass


def download(torrent):
    """
    Download torrent

    @param torrent:
    @return:
    """
    xbmc.executebuiltin('RunPlugin(plugin://plugin.video.yatp/?action=download&torrent={0})'.format(quote(torrent)))


def torrent_info(title, size, seeders, leechers):
    """
    Show torrent info

    @param title:
    @param size:
    @param seeders:
    @param leechers:
    @return:
    """
    xbmcgui.Dialog().ok('Torrent info',
                        'Name: ' + title,
                        'Size: {0}MB; seeders: {1}; leechers {2}'.format(size, seeders, leechers))


def clear_cache():
    """
    Clear page cache
    """
    if xbmcgui.Dialog().yesno('Rarbg TV Shows', 'Do you really want to clear the plugin cache?'):
        cache = os.path.join(_config_dir, 'cache.pcl')
        xbmcvfs.delete(cache)
        if not xbmcvfs.exists(cache):
            xbmcgui.Dialog().notification('Rarbg', 'Plugin cache cleared successfully.', _icon, 3000)


def clear_data():
    """
    Clear all plugin persistent data
    """
    if xbmcgui.Dialog().yesno('Rarbg TV Shows', 'Do you really want to clear all the plugin data?'):
        folders, files = xbmcvfs.listdir(_config_dir)
        deleted = True
        for file_ in files:
            if file_[-3:] == 'pcl':
                path = os.path.join(_config_dir, file_)
                xbmcvfs.delete(path)
                if xbmcvfs.exists(path):
                    deleted = False
        if deleted:
            xbmcgui.Dialog().notification('Rarbg', 'Plugin data cleared successfully.', _icon, 3000)


if __name__ == '__main__':
    if sys.argv[1] == 'myshows_add':
        add_to_favorites(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'myshows_remove':
        remove_from_favorites(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_strm':
        create_strm(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    elif sys.argv[1] == 'download':
        download(sys.argv[2])
    elif sys.argv[1] == 'clear_cache':
        clear_cache()
    elif sys.argv[1] == 'torrent_info':
        torrent_info(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'clear_data':
        clear_data()
    else:
        raise RuntimeError('Unknown command!')
