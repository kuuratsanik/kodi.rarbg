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
import fanarttv

_plugin = Plugin()


def _add_thetvdb_data_(torrents):
    """
    Add basic TV show data from TheTVDB

    @param torrents:
    @return:
    """
    results = OrderedDict()
    with _plugin.get_storage('tvshows.pcl') as tvshows:
        with _plugin.get_storage('episodes.pcl') as episodes:
            for torrent in torrents:
                if (torrent.get('episode_info') is None or
                            torrent['episode_info'].get('tvdb') is None or
                            torrent['episode_info']['tvdb'] is None):
                    continue
                ep_name_match = re.match(r'(.+?\.s\d+e\d+)\.', torrent['title'].lower())
                if ep_name_match is not None:
                    ep_name = ep_name_match.group(1)
                else:
                    ep_name = torrent['title'].lower()
                if ep_name not in results or torrent['seeders'] > results[ep_name]['seeders']:
                    imdb = torrent['episode_info']['imdb']
                    try:
                        show_info = tvshows[imdb]
                    except KeyError:
                        show_info = thetvdb.get_series(torrent['episode_info']['tvdb'])
                        art = fanarttv.get_art(torrent['episode_info']['tvdb'])
                        if art.get('clearlogo'):
                            show_info['clearlogo'] = art['clearlogo'][0]['url']
                        elif art.get('hdtvlogo'):
                            show_info['clearlogo'] = art['hdtvlogo'][0]['url']
                        if art.get('clearart'):
                            show_info['clearart'] = art['clearart'][0]['url']
                        elif art.get('hdclearart'):
                            show_info['clearart'] = art['hdclearart'][0]['url']
                        if art.get('tvthumb'):
                            show_info['landscape'] = art['tvthumb'][0]['url']
                        tvshows[imdb] = show_info
                    torrent['show_info'] = show_info
                    if torrent['episode_info'].get('epnum'):
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
                        _plugin.log(str(episode_info))
                        if episode_info is not None:
                            torrent['episode_info']['episode_name'] = episode_info['episode_name']
                            torrent['episode_info']['plot'] = episode_info['plot']
                            torrent['episode_info']['thumb'] = episode_info['thumb']
                    results[ep_name] = torrent
    return results.values()


def get_torrents(params):
    """
    Get recent torrents with TheTVDB data

    @return:
    """
    return _add_thetvdb_data_(rarbg.get_torrents(params))
