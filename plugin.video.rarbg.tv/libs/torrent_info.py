# -*- coding: utf-8 -*-
# Module: torrent_info
# Author: Roman V.M.
# Created on: 18.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Add extended info to torrents"""

import re
from collections import OrderedDict
from simpleplugin import Plugin
import rarbg
import thetvdb

_plugin = Plugin()


def _add_thetvdb_data_(torrents):
    """
    Add basic TV show data from TheTVDB

    :param torrents:
    :return:
    """
    results = OrderedDict()
    with _plugin.get_storage('tvshows.pcl') as tvshows:
        for torrent in torrents:
            ep_name_match = re.match(r'(.+?\.s\d+e\d+)\.', torrent['title'].lower())
            if ep_name_match is not None:
                ep_name = ep_name_match.group(1)
            else:
                ep_name = torrent['title'].lower()
            if ep_name not in results or torrent['seeders'] > results[ep_name]['seeders']:
                if torrent['episode_info'] is not None:
                    imdb = torrent['episode_info']['imdb']
                    try:
                        show_info = tvshows[imdb]
                    except KeyError:
                        show_info = thetvdb.get_series_by_imdbid(imdb)
                        tvshows[imdb] = show_info
                else:
                    show_info = None
                torrent['show_info'] = show_info
                results[ep_name] = torrent
    return results.values()


def get_torrents(params):
    """
    Get recent torrents with TheTVDB data

    :return:
    """
    return _add_thetvdb_data_(rarbg.get_torrents(params))
