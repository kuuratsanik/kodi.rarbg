# -*- coding: utf-8 -*-
# Module: torrent_info
# Author: Roman V.M.
# Created on: 18.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Add extended info to torrents"""

import sys
import os
import re
import threading
from collections import namedtuple
from xbmc import LOGERROR
from simpleplugin import Plugin
import tvdb
from rarbg import load_torrents
from exceptions import NoDataError

__all__ = ['get_torrents']

plugin = Plugin()

try:
    from collections import OrderedDict
except ImportError:
    sys.path.append(os.path.join(plugin.path, 'site-packages'))
    from ordereddict import OrderedDict

episode_regexes = (
    re.compile(r'(.+?)\.s(\d+)e(\d+)\.', re.IGNORECASE),
    re.compile(r'(.+?)\.(\d+)x(\d+)\.', re.IGNORECASE)
)
EpData = namedtuple('EpData', ['name', 'season', 'episode'])
lock = threading.Lock()


def parse_torrent_name(name):
    """
    Check a torrent name if this is an episode

    :param name: torrent name
    :type name: str
    :returns: episode data: name, season, episode
    :rtype: EpData
    :raises: ValueError if episode pattern is not matched
    """
    for regex in episode_regexes:
        match = re.match(regex, name)
        if match is not None:
            break
    else:
        raise ValueError
    return EpData(match.group(1), match.group(2), match.group(3))


def add_show_info(torrent, tvshows):
    """
    Add show info from TheTVDB to the torrent

    :param torrent: a torrent object from Rarbg
    :type torrent: dict
    :param tvshows: TV shows database with info from TheTVDB
    :type tvshows: dict
    """
    tvdbid = torrent['episode_info']['tvdb']
    try:
        show_info = tvshows[tvdbid]
        if show_info is None:
            raise KeyError
    except KeyError:
        try:
            show_info = tvdb.get_series(tvdbid)
        except NoDataError:
            plugin.log('TheTVDB rerturned no data for ID {0}, torrent {1}'.format(tvdbid, torrent['title']), LOGERROR)
            show_info = None
        else:
            show_info['IMDB_ID'] = torrent['episode_info']['imdb']  # This fix is mostly for the new "The X-Files"
            tvshows[tvdbid] = show_info
    with lock:
        torrent['show_info'] = show_info


def add_episode_info(torrent, episodes):
    """
    Add episode info from TheTVDB to the torrent

    :param torrent: a torrent object from Rarbg
    :type torrent: dict
    :param episodes: TV episodes database with info from TheTVDB
    :type episodes: dict
    """
    tvdbid = torrent['episode_info']['tvdb']
    episode_id = '{0}-{1}x{2}'.format(tvdbid,
                                      torrent['episode_info']['seasonnum'],
                                      torrent['episode_info']['epnum'])
    try:
        episode_info = episodes[episode_id]
        if episode_info is None:
            raise KeyError
    except KeyError:
        try:
            episode_info = tvdb.get_episode(tvdbid,
                                            torrent['episode_info']['seasonnum'],
                                            torrent['episode_info']['epnum'])
        except NoDataError:
            plugin.log('TheTVDB returned no data for episode {0}, torrent {1}'.format(episode_id, torrent['title']),
                       LOGERROR)
            episode_info = None
        else:
            episodes[episode_id] = episode_info
    with lock:
        torrent['tvdb_episode_info'] = episode_info


def deduplicate_torrents(torrents):
    """
    Deduplicate torrents from rarbg based on max. seeders

    :param torrents: raw torrent list from Rarbg
    :type torrents: list
    :return: deduplicated torrents generator
    :rtype: generator
    """
    results = OrderedDict()
    with plugin.get_storage('tvshows.pcl') as tvshows, plugin.get_storage('episodes.pcl ') as episodes:
        for torrent in torrents:
            if (torrent.get('episode_info') is None or
                        torrent['episode_info'].get('tvdb') is None or
                        torrent['episode_info'].get('imdb') is None):
                continue  # Skip an item if it's missing from IMDB or TheTVDB
            if torrent['episode_info'].get('seasonnum') is None or torrent['episode_info'].get('epnum') is None:
                try:
                    episode_data = parse_torrent_name(torrent['title'].lower())
                except ValueError:
                    continue
                else:
                    torrent['episode_info']['seasonnum'] = episode_data.season
                    torrent['episode_info']['epnum'] = episode_data.episode
            ep_id = (torrent['episode_info']['tvdb'] +
                     torrent['episode_info']['seasonnum'] + torrent['episode_info']['epnum'])
            if '.720' in torrent['title'] or '.1080' in torrent['title']:
                ep_id += 'hd'
            replace = False
            if ep_id not in results:
                add_episode_thread = threading.Thread(target=add_episode_info, args=(torrent, episodes))
                add_episode_thread.daemon = True
                add_episode_thread.start()
                add_show_info(torrent, tvshows)
                if add_episode_thread.is_alive():
                    add_episode_thread.join()
                replace = True
            elif torrent['seeders'] > results[ep_id]['seeders']:
                torrent['show_info'] = results[ep_id]['show_info'].copy()
                torrent['tvdb_episode_info'] = results[ep_id]['tvdb_episode_info'].copy()
                replace = True
            if replace:
                results[ep_id] = torrent
        return results.itervalues()


def get_torrents(mode, category='', search_string='', search_imdb=''):
    """
    Get torrents from Rarbg.to

    :param mode: Rarbg query mode -- 'list' or 'search'
    :type mode: str
    :param category: Rarbg torrents category
    :type category: str
    :param search_string: search query
    :type search_string: str
    :param search_imdb: imdb code for a TV show as ttXXXXX
    :type search_imdb: str
    :return: deduplicated episode torrents generator with TheTVDB data for shows and episodes
    :rtype: generator
    """
    rarbg_query = {'mode': mode, 'limit': plugin.itemcount}
    if plugin.get_setting('ignore_weak'):
        rarbg_query['min_seeders'] = plugin.get_setting('min_seeders', False)
    if category:
        rarbg_query['category'] = category
    if search_string:
        rarbg_query['search_string'] = search_string
    if search_imdb:
        rarbg_query['search_imdb'] = search_imdb
    try:
        raw_torrents = load_torrents(rarbg_query)
    except NoDataError:
        return []
    else:
        return deduplicate_torrents(raw_torrents)
