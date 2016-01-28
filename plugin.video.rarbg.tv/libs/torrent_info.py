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
from traceback import format_exc
from collections import namedtuple
from xbmc import LOGERROR
from simpleplugin import Plugin
import rarbg
import thetvdb

_plugin = Plugin()

sys.path.append(os.path.join(_plugin.path, 'site-packages'))
from ordereddict import OrderedDict

episode_regexes = (re.compile(r'(.+?)\.s(\d+)e(\d+)\.', re.IGNORECASE),
                   re.compile(r'(.+?)\.(\d+)x(\d+)\.'), re.IGNORECASE)


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
        raise ValueError('Episode name is not matched!')
    EpData = namedtuple('EpData', ['name', 'season', 'episode'])
    return EpData(match.group(1), match.group(2), match.group(3))


class ThreadPool(object):
    """
    Thread pool class
    """
    daemon_threads = True
    thread_count = 4

    def __init__(self):
        self._pool = [None] * self.thread_count

    def put(self, func, *args, **kwargs):
        """
        Put a function into the thread pool

        If all available threads are busy, the call will block.
        """
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = self.daemon_threads
        slot = self._get_free_slot()
        thread.start()
        self._pool[slot] = thread

    def _get_free_slot(self):
        while True:
            slot = -1
            for i, thread in enumerate(self._pool):
                if self._pool[i] is None or not thread.is_alive():
                    slot = i
                    break
            if slot >= 0:
                return slot
            time.sleep(0.1)

    def is_all_finished(self):
        """
        Check if there are no more active threads
        """
        for thread in self._pool:
            if thread is not None and thread.is_alive():
                return False
        return True


ThreadPool.thread_count = _plugin.thread_count
thread_pool = ThreadPool()
lock = threading.Lock()


def _add_show_info(torrent, tvshows):
    """
    Add show info from TheTVDB to the torrent
    """
    imdb = torrent['episode_info']['imdb']
    try:
        show_info = tvshows[imdb]
    except KeyError:
        show_info = thetvdb.get_series_by_imdbid(imdb)
        with lock:
            tvshows[imdb] = show_info
    with lock:
        torrent['show_info'] = show_info


def _add_episode_info(torrent, episodes):
    """
    Add episode info from TheTVDB to the torrent
    """
    imdb = torrent['episode_info']['imdb']
    episode_id = '{0}-{1}x{2}'.format(imdb,
                                      torrent['episode_info']['seasonnum'],
                                      torrent['episode_info']['epnum'])
    try:
        episode_info = episodes[episode_id]
    except KeyError:
        episode_info = thetvdb.get_episode(torrent['episode_info']['tvdb'],
                                           torrent['episode_info']['seasonnum'],
                                           torrent['episode_info']['epnum'])
        with lock:
            episodes[episode_id] = episode_info
    with lock:
        torrent['tvdb_episode_info'] = episode_info


def _add_tvdb_info(torrents):
    """
    Add TV show and episode data from TheTVDB
    """
    tvshows = _plugin.get_storage('tvshows.pcl')
    episodes = _plugin.get_storage('episodes.pcl')
    try:
        for torrent in torrents:
            thread_pool.put(_add_show_info, torrent, tvshows)
            thread_pool.put(_add_episode_info, torrent, episodes)
        while not thread_pool.is_all_finished():
            time.sleep(0.1)
    except:
        _plugin.log('Error when processing TV shows info:', LOGERROR)
        _plugin.log(format_exc(), LOGERROR)
    finally:
        tvshows.flush()
        episodes.flush()


def _deduplicate_data(torrents):
    """
    Deduplicate data from rarbg based on max seeders

    @param torrents:
    @return:
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
            ep_id = torrent['title'].lower()
        else:
            if not torrent['episode_info'].get('seasonnum'):
                torrent['episode_info']['seasonnum'] = episode_data.season
            if not torrent['episode_indo'].get('epnum'):
                torrent['episode_info']['epnum'] = episode_data.episode
            ep_id = episode_data.name + episode_data.season + episode_data.episode
            if '.720' in torrent['title'] or '.1080' in torrent['title']:
                ep_id += 'hd'
        if ep_id not in results or torrent['seeders'] > results[ep_id]['seeders']:
            results[ep_id] = torrent
    return results.values()


def get_torrents(params):
    """
    Get recent torrents with TheTVDB data

    @return:
    """
    torrents = _deduplicate_data(rarbg.get_torrents(params))
    _add_tvdb_info(torrents)
    return torrents
