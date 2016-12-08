# coding: utf-8
# Created on: 24.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import re
import cPickle as pickle
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


def check_episode_id(episode_id, tvdb, downloaded_episodes):
    return (tvdb not in downloaded_episodes or
            (tvdb in downloaded_episodes and episode_id not in downloaded_episodes[tvdb]))


def check_extra_filter(filters, torrent, tvdb):
    has_extra_filter = filters[tvdb].get('extra_filter')
    return (not has_extra_filter or
            (has_extra_filter and re.search(filters[tvdb]['extra_filter'], torrent['title'], re.I)))


def check_exclude(filters, torrent, tvdb):
    has_exclude = filters[tvdb].get('exclude')
    return not has_exclude or (has_exclude and not re.search(filters[tvdb]['exclude'], torrent['title'], re.I))


def filter_torrents():
    """
    Filter episode torrents from Rarbg by given criteria
    """
    torrents = get_torrents('list', limit='50', show_info=False, episode_info=False)
    filters = load_filters()
    with addon.get_storage('downloaded_episodes.pcl') as downloaded_episodes:
        for torrent in torrents:
            tvdb = torrent['episode_info']['tvdb']
            if tvdb in filters:
                episode_id = (int(torrent['episode_info']['seasonnum']),
                              int(torrent['episode_info']['epnum']),
                              check_proper(torrent['title']))
                if (check_episode_id(episode_id, tvdb, downloaded_episodes) and
                        check_extra_filter(filters, torrent, tvdb) and
                        check_exclude(filters, torrent, tvdb)):
                    download_torrent(torrent['download'], filters[tvdb]['save_path'])
                    if tvdb not in downloaded_episodes:
                        downloaded_episodes[tvdb] = []
                    downloaded_episodes[tvdb].append(episode_id)
                    addon.log_notice('Torrent {0} added for downloading'.format(torrent['title']))
