# coding: utf-8
# Created on: 24.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import re
import cPickle as pickle
from requests import post
from simpleplugin import Addon
from torrent_info import get_torrents, OrderedDict

addon = Addon()
yatp_addon = Addon('plugin.video.yatp')

filters_file = os.path.join(addon.config_dir, 'filters.json')
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


def filter_torrents():
    """
    Filter episode torrents from Rarbg by given criteria

    :return: ``True`` if at least one matching torrent found
    :rtype: bool
    """
    torrents = get_torrents('list', limit='50', add_info=False)
    filters = load_filters()
    torrents_found = False
    for torrent in torrents:
        tvdb = torrent['episode_info']['tvdb']
        if tvdb in filters:
            if ((filters[tvdb].get('extra_filter') and not re.search(filters[tvdb]['extra_filter'],
                                                                     torrent['title'],
                                                                     re.I | re.U)) or
                    (filters[tvdb].get('exclude') and re.search(filters[tvdb]['exclude'],
                                                                torrent['title'],
                                                                re.I | re.U))):
                continue
            else:
                download_torrent(torrent['download'], filters[tvdb]['save_path'])
                del filters[tvdb]
                torrents_found = True
    return torrents_found
