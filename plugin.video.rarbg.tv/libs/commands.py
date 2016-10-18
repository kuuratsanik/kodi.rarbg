# -*- coding: utf-8 -*-
# Module: commands
# Author: Roman V.M.
# Created on: 19.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

"""Commands called via context menu"""

import sys
import os
import xbmcgui
import xbmc
import xbmcvfs
from simpleplugin import Plugin
from autodownloader import load_filters, save_filters, download_torrent

plugin = Plugin('plugin.video.rarbg.tv')


def clean_files(pattern):
    """
    Clean files by the specified pattern

    :param pattern: a pattern to search for in filenames
    :type pattern: str
    :return: celeaning result
    :rtype: bool
    """
    folders, files = xbmcvfs.listdir(plugin.config_dir)
    deleted = True
    for file_ in files:
        if pattern in file_:
            path = os.path.join(plugin.config_dir, file_)
            xbmcvfs.delete(path)
            if xbmcvfs.exists(path):
                deleted = False
    return deleted


def add_to_favorites(tvdb):
    """
    Add a TV Show to favorites

    :param tvdb: str - TheTVDB ID
    :return:
    """
    with plugin.get_storage('myshows.pcl') as storage:
        mshows = storage.get('myshows', [])
        if tvdb not in mshows:
            mshows.append(tvdb)
            storage['myshows'] = mshows
            xbmcgui.Dialog().notification('Rarbg', 'The show successfully added to "My Shows"',
                                          plugin.icon, 3000, sound=False)
        else:
            xbmcgui.Dialog().notification('Rarbg', 'The show is already in "My Shows"!', 'error', 3000)


def remove_from_favorites(index):
    """
    Remove a TV show from "My Shows"

    :param index: str - digital index of the item to be removed
    :return:
    """
    with plugin.get_storage('myshows.pcl') as storage:
        del storage['myshows'][int(index)]
    xbmcgui.Dialog().notification('Rarbg', 'The show removed from "My Shows"', plugin.icon, 3000, sound=False)
    xbmc.executebuiltin('Container.Refresh')


def create_strm(filename, torrent, poster, title, season, episode):
    """
    Create a .strm file for torrent

    :param filename:
    :param torrent:
    :return:
    """
    # todo: finish this
    pass


def download(torrent, show_title):
    """
    Download torrent

    :param torrent:
    :return:
    """
    if plugin.download_dir:
        download_torrent(torrent, os.path.join(plugin.download_dir, show_title))
        xbmcgui.Dialog().notification('Rarbg', 'Torrent added to YATP for downloading.',
                                      plugin.icon, 3000, sound=False)
    elif not plugin.downlaod_dir and xbmcgui.Dialog().yesno('Rarbg', 'To download torrent you need',
                                                           'to set base download directory first!',
                                                           'Open plugin settings?'):
        plugin.addon.openSettings()


def torrent_info(title, size, seeders, leechers):
    """
    Show torrent info

    :param title:
    :param size:
    :param seeders:
    :param leechers:
    :return:
    """
    xbmcgui.Dialog().ok('Torrent info',
                        'Name: ' + title,
                        'Size: {0}MB; seeders: {1}; leechers {2}'.format(size, seeders, leechers))


def clear_cache():
    """
    Clear page cache
    """
    if xbmcgui.Dialog().yesno('Rarbg TV Shows', 'Do you really want to clear the plugin cache?'):
        if clean_files('cache.'):
            xbmcgui.Dialog().notification('Rarbg', 'Plugin cache cleared successfully.',
                                          plugin.icon, 3000, sound=False)


def clear_data():
    """
    Clear all plugin persistent data
    """
    if xbmcgui.Dialog().yesno('Rarbg TV Shows', 'Do you really want to clear all the plugin data?'):
        if clean_files('.pcl'):
            xbmcgui.Dialog().notification('Rarbg', 'Plugin data cleared successfully.',
                                          plugin.icon, 3000, sound=False)


def add_filter(tvdb, show_title):
    """
    Add filter for episode autodownloading
    """
    filters = load_filters()
    if plugin.download_dir and tvdb not in filters:
        filters[tvdb] = {
            'name': show_title,
            'save_path': os.path.join(plugin.download_dir, show_title),
            'extra_filter': '',
            'exclude': ''
            }
        save_filters(filters)
        xbmcgui.Dialog().notification('Rarbg', 'Added download filter for {0}'.format(show_title),
                                      plugin.icon, sound=False)
    elif tvdb in filters:
        xbmcgui.Dialog().notification('Rarbg', 'The show {0} is already set for downloading!'.format(show_title), 
                                      plugin.icon)
    elif not plugin.download_dir and xbmcgui.Dialog().yesno('Rarbg',
                                                            'To add episode download filter',
                                                            'you need to set base download directory first!',
                                                            'Open plugin settings?'):
        plugin.addon.openSettings()


if __name__ == '__main__':
    if sys.argv[1] == 'myshows_add':
        add_to_favorites(sys.argv[2])
    elif sys.argv[1] == 'myshows_remove':
        remove_from_favorites(sys.argv[2])
    elif sys.argv[1] == 'create_strm':
        create_strm(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    elif sys.argv[1] == 'download':
        download(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'clear_cache':
        clear_cache()
    elif sys.argv[1] == 'torrent_info':
        torrent_info(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'clear_data':
        clear_data()
    elif sys.argv[1] == 'add_filter':
        add_filter(sys.argv[2], sys.argv[3])
    else:
        raise RuntimeError('Unknown command!')
