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
import time
from collections import namedtuple
from xbmc import LOGERROR
from simpleplugin import Plugin
import tvdb
import rarbg
from utilities import ThreadPool
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
    :returns: episode data: name, season, episode
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
    except KeyError:
        try:
            show_info = tvdb.get_series(tvdbid)
        except NoDataError:
            plugin.log('TheTVDB rerturned no data for ID {0}, torrent {1}'.format(tvdbid, torrent['title']), LOGERROR)
            show_info = None
        else:
            show_info['IMDB_ID'] = torrent['episode_info']['imdb']  # This fix is mostly for the new "The X-Files"
            with lock:
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
    except KeyError:
        try:
            episode_info = tvdb.get_episode(tvdbid,
                                            torrent['episode_info']['seasonnum'],
                                            torrent['episode_info']['epnum'])
        except NoDataError:
            plugin.log('TheTVDB returned no data for episode {0}, torrent {1}'.format(episode_id, torrent['title']))
            episode_info = None
        else:
            with lock:
                episodes[episode_id] = episode_info
    with lock:
        torrent['tvdb_episode_info'] = episode_info


def add_tvdb_info(torrents):
    """
    Add TV show and episode data from TheTVDB to torrents

    :param torrents: the list of torrents from Rarbg as dicts
    :type torrents: list
    """
    tvshows = plugin.get_storage('tvshows.pcl')
    episodes = plugin.get_storage('episodes.pcl')
    ThreadPool.thread_count = plugin.thread_count
    thread_pool = ThreadPool()
    try:
        for torrent in torrents:
            thread_pool.put(add_show_info, torrent, tvshows)
            thread_pool.put(add_episode_info, torrent, episodes)
        while not thread_pool.is_all_finished():
            time.sleep(0.1)
    finally:
        tvshows.flush()
        episodes.flush()


def deduplicate_torrents(torrents):
    """
    Deduplicate torrents from rarbg based on max. seeders

    :param torrents: raw torrent list from Rarbg
    :type torrents: list
    :return: deduplicated torrents list
    :rtype: list
    """
    results = OrderedDict()
    for torrent in torrents:
        if (torrent.get('episode_info') is None or
                    torrent['episode_info'].get('tvdb') is None or
                    torrent['episode_info'].get('imdb') is None):
            continue  # Skip an item if it's missing from IMDB or TheTVDB
        try:
            episode_data = parse_torrent_name(torrent['title'].lower())
        except ValueError:
            if torrent['episode_info'].get('epnum') is None:
                continue
        else:
            if not torrent['episode_info'].get('seasonnum'):
                torrent['episode_info']['seasonnum'] = episode_data.season
            if not torrent['episode_info'].get('epnum'):
                torrent['episode_info']['epnum'] = episode_data.episode
        ep_id = torrent['episode_info']['tvdb'] + torrent['episode_info']['seasonnum'] + torrent['episode_info']['epnum']
        if '.720' in torrent['title'] or '.1080' in torrent['title']:
            ep_id += 'hd'
        if ep_id not in results or torrent['seeders'] > results[ep_id]['seeders']:
            results[ep_id] = torrent
    return results.values()


def get_torrents(query):
    """
    Get recent torrents with TheTVDB data

    :param query: query to Rarbg
    :type query: dict
    :return: deduplicated episode torrents list with TheTVDB data for shows and episodes
    :rtype: list
    """
    torrents = deduplicate_torrents(rarbg.get_torrents(query))
    add_tvdb_info(torrents)
    return torrents
