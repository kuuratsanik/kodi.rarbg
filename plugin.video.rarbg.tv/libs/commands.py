# -*- coding: utf-8 -*-
# Module: commands
# Author: Roman V.M.
# Created on: 19.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

# Commands called via context menu

import sys
import os
from cPickle import load, dump, PickleError
#
import xbmcgui
import xbmc

def add_to_favorites(config_dir, title, imdb, poster):
    """
    Add a TV Show to favorites
    :param config_dir: str - Addon config folder
    :param title: str - TV show title
    :param imdb: str - IMDB ID (tt1234567)
    :return:
    """
    storage = {}
    filename = os.path.join(config_dir, 'storage.pcl')
    if os.path.exists(filename):
        mode = 'r+b'
    else:
        mode = 'w+b'
    with open(filename, mode) as file_:
        try:
            storage = load(file_)
        except (PickleError, EOFError):
            pass
        try:
            my_shows = storage['myshows']
        except KeyError:
            my_shows = []
        if imdb not in [item[1] for item in my_shows]:
            my_shows.append((title, imdb, poster))
            storage['myshows'] = my_shows
            file_.seek(0)
            dump(storage, file_)
            file_.truncate()
            xbmcgui.Dialog().notification('Note!', 'The show added to "My Shows"', 'info', 3000)
        else:
            xbmcgui.Dialog().notification('Error!', 'The show already in "My Shows".', 'error', 3000)


def remove_from_favorites(config_dir, index):
    """
    Remove a TV show from "My Shows"
    :param config_dir: str - Addon config folder
    :param index: str - digital index of the item to be removed
    :return:
    """
    filename = os.path.join(config_dir, 'storage.pcl')
    with open(filename, 'r+b') as file_:
        storage = load(file_)
        del storage['myshows'][int(index)]
        file_.seek(0)
        dump(storage, file_)
        file_.truncate()
    xbmcgui.Dialog().notification('Note!', 'The show removed from "My Shows"', 'info', 3000)
    xbmc.executebuiltin('Container.Refresh')


if __name__ == '__main__':
    if sys.argv[1] == 'myshows_add':
        add_to_favorites(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'myshows_remove':
        remove_from_favorites(sys.argv[2], sys.argv[3])
