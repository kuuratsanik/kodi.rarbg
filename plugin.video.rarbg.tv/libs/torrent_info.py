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
from rarbg_exceptions import NoDataError

__all__ = ['get_torrents', 'OrderedDict']

plugin = Plugin('plugin.video.rarbg.tv')

try:
    from collections import OrderedDict
except ImportError:
    sys.path.append(os.path.join(plugin.path, 'site-packages'))
    from ordereddict import OrderedDict

episode_regexes = (
    re.compile(r'^.+?\.s(\d+)e(\d+)\.', re.I | re.U),
    re.compile(r'^.+?\.(\d+)x(\d+)\.', re.I | re.U)
)
repack_regex = re.compile(r'^.+?\.(s\d+e\d+|\d+x\d+)\..*?(proper|repack).*?$', re.I | re.U)
EpData = namedtuple('EpData', ['season', 'episode'])
lock = threading.Lock()


def parse_torrent_name(name):
    """
    Check a torrent name if this is an episode

    :param name: torrent name
    :type name: str
    :returns: season #, episode #
    :rtype: EpData
    :raises: ValueError if episode pattern is not matched
    """
    for regex in episode_regexes:
        match = re.search(regex, name)
        if match is not None:
            break
    else:
        raise ValueError
    return EpData(match.group(1), match.group(2))


def add_show_info(torrent, tvshows):
    """
    Add show info from TheTVDB to the torrent

    :param torrent: a torrent object from Rarbg
    :type torrent: dict
    :param tvshows: TV shows database with info from TheTVDB
    :type tvshows: dict
    """
    tvdbid = torrent['episode_info']['tvdb']
    show_info = tvshows.get(tvdbid)
    if show_info is None:
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
    episode_info = episodes.get(episode_id)
    if episode_info is None:
        try:
            episode_info = tvdb.get_episode(tvdbid,
                                            torrent['episode_info']['seasonnum'],
                                            torrent['episode_info']['epnum'])
        except NoDataError:
            plugin.log('TheTVDB returned no data for episode {0}, torrent {1}'.format(episode_id, torrent['title']))
            episode_info = None
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
        if torrent['episode_info'].get('seasonnum') is None or torrent['episode_info'].get('epnum') is None:
            try:
                episode_data = parse_torrent_name(torrent['title'].lower())
            except ValueError:
                continue
            else:
                torrent['episode_info']['seasonnum'] = episode_data.season
                torrent['episode_info']['epnum'] = episode_data.episode
        ep_id = torrent['episode_info']['tvdb'] + torrent['episode_info']['seasonnum'] + torrent['episode_info']['epnum']
        if '.720' in torrent['title'] or '.1080' in torrent['title']:
            ep_id += 'hd'
        if (ep_id not in results or
                    torrent['seeders'] > results[ep_id]['seeders'] or
                    re.match(repack_regex, torrent['title']) is not None):
            results[ep_id] = torrent
    return results.values()


def get_torrents(mode, search_string='', search_imdb='', limit='', add_info=True):
    """
    Get recent torrents with TheTVDB data

    :param mode: Rarbg query mode -- 'list' or 'search'
    :type mode: str
    :param search_string: search query
    :type search_string: str
    :param search_imdb: imdb code for a TV show as ttXXXXX
    :type search_imdb: str
    :param limit: max number of torrents from Rarbg
    :type limit: str
    :param add_info: add info from TheTVDB to torrents
    :type add_info: bool
    :return: the list of torrents matching the query criteria
    :rtype: list
    """
    rarbg_query = {'mode': mode, 'category': ('18;41', '18', '41')[plugin.quality]}
    if plugin.get_setting('ignore_weak'):
        rarbg_query['min_seeders'] = plugin.get_setting('min_seeders', False)
    if search_string:
        rarbg_query['search_string'] = search_string
    if search_imdb:
        rarbg_query['search_imdb'] = search_imdb
    if limit:
        rarbg_query['limit'] = limit
    else:
        rarbg_query['limit'] = plugin.itemcount
    try:
        raw_torrents = rarbg.load_torrents(rarbg_query)
    except NoDataError:
        return []
    else:
        torrents = deduplicate_torrents(raw_torrents)
        if add_info:
            add_tvdb_info(torrents)
        return torrents
