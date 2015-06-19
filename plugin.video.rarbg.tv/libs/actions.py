# -*- coding: utf-8 -*-
# Module: actions
# Author: Roman V.M.
# Created on: 09.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
import base64
import re
import urllib
import xbmc
import xbmcgui
from simpleplugin import Plugin
import torrent_info

plugin = Plugin()
_icons = os.path.join(plugin.path, 'resources', 'icons')


@plugin.cached(15)
def _get_torrents(mode, category='', search_sthring='', search_imdb=''):
    rarbg_params = {'mode': mode, 'limit': plugin.get_setting('itemcount')}
    if plugin.get_setting('ignore_weak'):
        rarbg_params['min_seeders'] = plugin.get_setting('min_seeders')
    if category:
        rarbg_params['category'] = category
    if search_sthring:
        rarbg_params['search_string'] = search_sthring
    if search_imdb:
        rarbg_params['imdb'] = search_sthring
    return torrent_info.get_torrents(rarbg_params)


def _list_torrents(torrents):
    """
    Show the list of torrents
    :param torrents: list
    :return:
    """
    listing = [{'label': '<< Home',
                'thumb': os.path.join(_icons, 'home.png'),
                'icon': os.path.join(_icons, 'home.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url()}]
    for torrent in torrents:
        plugin.log(str(torrent))
        if torrent['seeders'] <= 10:
            seeders = '[COLOR=red]{0}[/COLOR]'.format(torrent['seeders'])
        elif torrent['seeders'] <= 25:
            seeders = '[COLOR=yellow]{0}[/COLOR]'.format(torrent['seeders'])
        else:
            seeders = str(torrent['seeders'])
        list_item = {'label': '{title} [COLOR=gray]({size}MB|S:{seeders}/L:{leechers})[/COLOR]'.format(
                                title=torrent['title'],
                                size=torrent['size'] / 1048576,
                                seeders=seeders,
                                leechers=torrent['leechers']),
                     'fanart': plugin.fanart,
                     'info': {},
                     'stream_info': {'video': {}},
                     'is_folder': False,
                     }
        video = {}
        if torrent['show_info'] is not None:
            video['tvshowtitle'] = torrent['show_info']['tvshowtitle']
            video['plot'] = torrent['show_info']['plot']
            video['year'] = int(torrent['show_info']['premiered'][:4])
            video['season'] = 0
            list_item['thumb'] = torrent['show_info']['banner']
            list_item['art'] = {}
            list_item['art']['banner'] = torrent['show_info']['banner']
        else:
            list_item['thumb'] = os.path.join(_icons, 'tv.png')
        if torrent['episode_info'] is not None and torrent['episode_info'].get('title') is not None:
            # video['title'] = torrent['episode_info']['title'] - Screws a list in Aeon-Shednox
            video['season'] = int(torrent['episode_info']['seasonnum'])
            video['episode'] = int(torrent['episode_info']['epnum'])
            video['aired'] = torrent['episode_info']['airdate']
        else:
            se_match = re.search(r'\.[Ss](\d+)[Ee]?(\d+)?', torrent['title'])
            if se_match is None:
                se_match = re.search(r'\.(\d+)[Xx](\d+)?', torrent['title'])
            if se_match is not None:
                video['season'] = int(se_match.group(1))
                try:
                    video['episode'] = int(se_match.group(2))
                except TypeError:
                    pass
        list_item['info']['video'] = video
        list_item['url'] = plugin.get_url(plugin.get_url('plugin://plugin.video.yatp/',
                                          action='play',
                                          torrent=base64.urlsafe_b64encode(torrent['download'].encode('utf-8')),
                                          title=base64.urlsafe_b64encode(video.get('tvshowtitle',
                                                                                   torrent['title']).encode('utf-8')),
                                          thumb=base64.urlsafe_b64encode(list_item['thumb'].encode('utf-8')),
                                          season=video.get('season', ''),
                                          episode=video.get('episode', '')))
        resolution_match = re.search(r'(720|1080)[pi]', torrent['title'].lower())
        if resolution_match is not None and resolution_match.group(1) == '720':
            list_item['stream_info']['video']['width'] = 1280
            list_item['stream_info']['video']['height'] = 720
        elif resolution_match is not None and resolution_match.group(1) == '1080':
            list_item['stream_info']['video']['width'] = 1920
            list_item['stream_info']['video']['height'] = 1080
        else:
            list_item['stream_info']['video']['width'] = 720
            list_item['stream_info']['video']['height'] = 480
        codec_match = re.search(r'[hx]\.?264', torrent['title'].lower())
        if codec_match is not None:
            list_item['stream_info']['video']['codec'] = 'h264'
        else:
            codec_match = re.search(r'xvid|divx', torrent['title'].lower())
            if codec_match is not None:
                list_item['stream_info']['video']['codec'] = codec_match.group(0)
        listing.append(list_item)
    if xbmc.getSkinDir() == 'skin.confluence':
        view_mode = 503
    else:
        view_mode = 50
    return plugin.create_listing(listing, content='episodes', view_mode=view_mode)


def root(params):
    """
    Plugin root
    :param params:
    :return:
    """
    listing = [{'label': '[Recent Episodes]',
                'thumb': os.path.join(_icons, 'tv.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='recent_episodes'),
                },
               {'label': '[Search torrents...]',
                'thumb': os.path.join(_icons, 'search.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='search_torrents')
               },
               ]
    return listing


def recent_episodes(params):
    """
    Show the list of recent episodes
    :param params:
    :return:
    """
    return _list_torrents(_get_torrents('list', category=('18;41', '18', '41',)[plugin.get_setting('quality')]))


def search_torrents(params):
    """
    Search torrents and show the list of results
    :param params:
    :return:
    """
    keyboard = xbmc.Keyboard('', 'Enter search text')
    keyboard.doModal()
    text = keyboard.getText()
    if keyboard.isConfirmed() and text:
        results = _get_torrents('search',
                                search_sthring=urllib.quote_plus(text),
                                category=('18;41', '18', '41',)[plugin.get_setting('quality')])
        if results:
            return _list_torrents(results)
        else:
            xbmcgui.Dialog().ok('Nothing found!', 'Adjust your search string and try again.')
    if xbmc.getSkinDir() == 'skin.confluence':
        view_mode = 503
    else:
        view_mode = 50
    return plugin.create_listing([], view_mode=view_mode)


# Map actions
plugin.actions['root'] = root
plugin.actions['recent_episodes'] = recent_episodes
plugin.actions['search_torrents'] = search_torrents
