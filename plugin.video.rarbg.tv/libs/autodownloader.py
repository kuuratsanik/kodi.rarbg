# coding: utf-8
# Created on: 24.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import re
import cPickle as pickle
from traceback import format_exc
from requests import post
from simpleplugin import Addon
from torrent_info import get_torrents, OrderedDict, check_proper

addon = Addon('plugin.video.rarbg.tv')
yatp_addon = Addon('plugin.video.yatp')

filters_file = os.path.join(addon.config_dir, 'filters.pcl')
json_rpc_url = 'http://127.0.0.1:{0}/json-rpc'.format(yatp_addon.server_port)


def download_torrent(torrent, save_path):
    """
    Download torrent via YATP
    """
    post(json_rpc_url, json={'method': 'add_torrent',
                             'params': {'torrent': torrent, 'save_path': save_path, 'paused': False}})


def load_filters():
    """
    Read episode filters from disk

    :return: filters
    :rtype: OrderedDict
    """
    try:
        with open(filters_file, mode='rb') as fo:
            filters = pickle.load(fo)
    except (IOError, EOFError, ValueError, pickle.PickleError):
        filters = OrderedDict()
    return filters


def save_filters(filters):
    """
    Save episode filters to disk

    :param filters: filters
    :type filters: OrderedDict
    """
    with open(filters_file, mode='wb') as fo:
        pickle.dump(filters, fo)


def check_episode(episode_id, episodes):
    """
    Check if an episode is in episode list

    :param episode_id: 3-element tuple (S, E, proper)
    :type episode_id: tuple
    :param episodes: the list of episode IDs
    :type episodes: list
    :return: check result
    :rtype: bool
    """
    for episode in episodes:
        if (episode_id[0], episode_id[1]) == (episode[0], episode[1]):
            addon.log_notice('Episode {0} already downloaded'.format(episode_id))
            return True
    addon.log_notice('New episode: {0}'.format(episode_id))
    return False


def check_episode_id(episode_id, tvdb, downloaded_episodes):
    """
    Check if an episode needs to be downloaded

    :param episode_id: 3-element tuple (S, E, proper)
    :type episode_id: tuple
    :param tvdb: TheTVDB ID
    :type tvdb: str
    :param downloaded_episodes: the collection of downloaded episode IDs
    :type downloaded_episodes: dict
    :return: check result
    :rtype: bool
    """
    addon.log_notice('Checking episode {0}'.format(episode_id))
    return (tvdb not in downloaded_episodes or
            (not check_episode(episode_id, downloaded_episodes[tvdb]) or episode_id[2]))


def check_extra_filter(filters, torrent, tvdb):
    """
    Check extra filter criteria

    :param filters: the collection of filters
    :type filters: OrderedDict
    :param torrent: the torrent to check
    :type torrent: dict
    :param tvdb: TheTVDB ID
    :type tvdb: str
    :return: check result
    :rtype: bool
    """
    has_extra_filter = filters[tvdb].get('extra_filter')
    return (not has_extra_filter or
            (has_extra_filter and re.search(filters[tvdb]['extra_filter'], torrent['title'], re.I)))


def check_exclude(filters, torrent, tvdb):
    """
    Check exclude filters

    :param filters: the collection of filters
    :type filters: OrderedDict
    :param torrent: the torrent to check
    :type torrent: dict
    :param tvdb: TheTVDB ID
    :type tvdb: str
    :return: check result
    :rtype: bool
    """
    has_exclude = filters[tvdb].get('exclude')
    return not has_exclude or (has_exclude and not re.search(filters[tvdb]['exclude'], torrent['title'], re.I))


def filter_torrents():
    """
    Filter episode torrents from Rarbg by given criteria
    """
    try:
        torrents = get_torrents('list', limit='50', show_info=False, episode_info=False)
    except:
        addon.log_error('Failed to load torrents from rarbg.to!')
        addon.log_error(format_exc())
        return
    filters = load_filters()
    with addon.get_storage('downloaded_episodes.pcl') as downloaded_episodes:
        for torrent in torrents:
            tvdb = torrent['episode_info']['tvdb']
            if tvdb in filters:
                episode_id = (int(torrent['episode_info']['seasonnum']),
                              int(torrent['episode_info']['epnum']),
                              check_proper(torrent['title']))
                addon.log_notice('Checking torrent {0}'.format(torrent))
                if (check_episode_id(episode_id, tvdb, downloaded_episodes) and
                        check_extra_filter(filters, torrent, tvdb) and
                        check_exclude(filters, torrent, tvdb)):
                    download_torrent(torrent['download'], filters[tvdb]['save_path'])
                    if tvdb not in downloaded_episodes:
                        downloaded_episodes[tvdb] = []
                    downloaded_episodes[tvdb].append(episode_id)
                    addon.log_notice('Torrent {0} added for downloading'.format(torrent['title']))
