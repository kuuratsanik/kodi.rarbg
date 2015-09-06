# -*- coding: utf-8 -*-
# Module: torrent_info
# Author: Roman V.M.
# Created on: 18.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Add extended info to torrents"""

import re
from ordereddict import OrderedDict
from simpleplugin import Plugin
import rarbg
import thetvdb

_plugin = Plugin()


def _add_thetvdb_data_(torrents):
    """
    Add TV show data from TheTVDB

    This function also deduplicates Rarbg results by picking an item
    with max seeders
    @param torrents:
    @return:
    """
    results = OrderedDict()
    with _plugin.get_storage('tvshows.pcl') as tvshows:
        with _plugin.get_storage('episodes.pcl') as episodes:
            for torrent in torrents:
                if (torrent.get('episode_info') is None or
                    torrent['episode_info'].get('epnum') is None or
                    torrent['episode_info'].get('imdb') is None or
                        torrent['episode_info']['tvdb'] is None):
                    continue  # Skip an item if it's not an episode or missing from TheTVDB
                ep_name_match = re.match(r'(.+?\.s\d+e\d+)\.', torrent['title'].lower())
                if ep_name_match is not None:
                    ep_name = ep_name_match.group(1)
                    if '720' in torrent['title'] or '1080' in torrent['title']:
                        ep_name += 'hd'
                else:
                    ep_name = torrent['title'].lower()
                if ep_name not in results or torrent['seeders'] > results[ep_name]['seeders']:
                    imdb = torrent['episode_info']['imdb']
                    try:
                        show_info = tvshows[imdb]
                    except KeyError:
                        show_info = thetvdb.get_series(torrent['episode_info']['tvdb'])
                        tvshows[imdb] = show_info
                    torrent['show_info'] = show_info
                    try:
                        episode_info = episodes[imdb +
                                                torrent['episode_info']['seasonnum'] +
                                                torrent['episode_info']['epnum']]
                    except KeyError:
                        episode_info = thetvdb.get_episode(torrent['episode_info']['tvdb'],
                                                           torrent['episode_info']['seasonnum'],
                                                           torrent['episode_info']['epnum'])
                        episodes[imdb + torrent['episode_info']['seasonnum'] +
                                 torrent['episode_info']['epnum']] = episode_info
                    torrent['tvdb_episode_info'] = episode_info
                    results[ep_name] = torrent
    return results.values()


def get_torrents(params):
    """
    Get recent torrents with TheTVDB data

    @return:
    """
    return _add_thetvdb_data_(rarbg.get_torrents(params))
