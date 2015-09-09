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


def add_to_favorites(config_dir, imdb):
    """
    Add a TV Show to favorites

    @param config_dir: str - Addon config folder
    @param title: str - TV show title
    @param imdb: str - IMDB ID (tt1234567)
    @param thumb: str - item's thumbnail image
    @return:
    """
    with Storage(config_dir, 'myshows.pcl') as storage:
        my_shows = storage.get('myshows', [])
        if imdb not in my_shows:
            my_shows.append(imdb)
            storage['myshows'] = my_shows
            xbmcgui.Dialog().notification('Rarbg', 'The show successfully added to "My Shows"', _icon, 3000)
        else:
            xbmcgui.Dialog().notification('Rarbg', 'The show already in "My Shows"!', 'error', 3000)


def remove_from_favorites(config_dir, index):
    """
    Remove a TV show from "My Shows"

    @param config_dir: str - Addon config folder
    @param index: str - digital index of the item to be removed
    @return:
    """
    print '********** plugin.video.rarbg.tv: Removing a show from My Shows: {}'.format(index)
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
    @return:
    """
    if xbmcgui.Dialog().yesno('Rarbg TV Shows', 'Do you really want to clear the plugin cache?'):
        xbmcvfs.delete('special://profile/addon_data/plugin.video.rarbg.tv/cache.pcl')
        if not xbmcvfs.exists('special://profile/addon_data/plugin.video.rarbg.tv/cache.pcl'):
            xbmcgui.Dialog().notification('Rarbg', 'Plugin cache cleared successfully.', _icon, 3000)


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
    else:
        raise RuntimeError('Unknown command!')
