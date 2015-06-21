# -*- coding: utf-8 -*-
# Module: commands
# Author: Roman V.M.
# Created on: 19.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

# Commands called via context menu

import sys
import os
from base64 import urlsafe_b64encode
#
import xbmcgui
import xbmc
import xbmcvfs
from simpleplugin import Storage

_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon.png')


def add_to_favorites(config_dir, title, thumb, imdb):
    """
    Add a TV Show to favorites
    :param config_dir: str - Addon config folder
    :param title: str - TV show title
    :param imdb: str - IMDB ID (tt1234567)
    :param thumb: str - item's thumbnail image
    :return:
    """
    with Storage(config_dir, 'myshows.pcl') as storage:
        my_shows = storage.get('myshows', [])
        if imdb not in [item[2] for item in my_shows]:
            my_shows.append((title, thumb, imdb))
            storage['myshows'] = my_shows
            xbmcgui.Dialog().notification('Rarbg', 'The show successfully added to "My Shows"', _icon, 3000)
        else:
            xbmcgui.Dialog().notification('Rarbg', 'The show already in "My Shows"!', 'error', 3000)


def remove_from_favorites(config_dir, index):
    """
    Remove a TV show from "My Shows"
    :param config_dir: str - Addon config folder
    :param index: str - digital index of the item to be removed
    :return:
    """
    with Storage(config_dir, 'myshows.pcl') as storage:
        del storage['myshows'][int(index)]
    xbmcgui.Dialog().notification('Rarbg', 'The show removed from "My Shows"', _icon, 3000)
    xbmc.executebuiltin('Container.Refresh')


def create_strm(filename, torrent, poster, title, season, episode):
    """
    Create a .strm file for torrent
    :param filename:
    :param torrent:
    :return:
    """
    dialog = xbmcgui.Dialog()
    folder = dialog.browse(0, 'Select a folder to save .strm', 'video')
    if folder:
        url = 'plugin://plugin.video.yatp/?action=play&torrent={0}&thumb={1}&title={2}'.format(
            urlsafe_b64encode(torrent),
            urlsafe_b64encode(poster),
            urlsafe_b64encode(title))
        if season:
            url += '&season=' + season
        if episode:
            url += '&episode' + episode
        with open(os.path.join(folder, filename + '.strm'), 'w') as file_:
            file_.write(url)
        dialog.notification('Rarbg', '.strm file created successfully', _icon, 3000)


def download(torrent):
    """
    Download torrent
    :param torrent:
    :return:
    """
    folder = xbmcgui.Dialog().browse(0, 'Select a folder to download the torrent', 'video')
    if folder:
        xbmc.executebuiltin('RunPlugin(plugin://plugin.video.yatp/?action=download&torrent={0}&save_path={1})'.format(
            urlsafe_b64encode(torrent),
            urlsafe_b64encode(folder)))


def clear_cache():
    """
    Clear page cache
    :return:
    """
    if xbmcgui.Dialog().yesno('Rarbg TV Shows', 'Do you really want to clear the plugin cache?'):
        xbmcvfs.delete('special://profile/addon_data/plugin.video.rarbg.tv/cache.pcl')
        if not xbmcvfs.exists('special://profile/addon_data/plugin.video.rarbg.tv/cache.pcl'):
            xbmcgui.Dialog().notification('Rarbg', 'Plugin cache cleared successfully.', _icon, 3000)


if __name__ == '__main__':
    if sys.argv[1] == 'myshows_add':
        add_to_favorites(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'myshows_remove':
        remove_from_favorites(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_strm':
        create_strm(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    elif sys.argv[1] == 'download':
        download(sys.argv[2])
    elif sys.argv[1] == 'clear_cache':
        clear_cache()
