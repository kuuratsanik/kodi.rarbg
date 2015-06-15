# -*- coding: utf-8 -*-
# Module: actions
# Author: Roman V.M.
# Created on: 09.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from urllib import quote_plus
import xbmc
import xbmcgui
from simpleplugin import Plugin
import parser

plugin = Plugin()
_icons = os.path.join(plugin.path, 'resources', 'icons')
_home = {'label': '<< Home',
         'thumb': os.path.join(_icons, 'home.png'),
         'icon': os.path.join(_icons, 'home.png'),
         'fanart': plugin.fanart,
         'url': plugin.get_url()}


def root(params):
    """
    Plugin root
    :param params:
    :return:
    """
    listing = [{'label': '[Recent Episodes]',
                'thumb': os.path.join(_icons, 'tv.png'),
                'icon': os.path.join(_icons, 'tv.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='episode_list', page='1'),
                },
               {'label': '[Search episodes...]',
                'thumb': os.path.join(_icons, 'search.png'),
                'icon': os.path.join(_icons, 'search.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='search_episodes', page='1'),
                },
               {'label': '[My Shows]',
                'thumb': os.path.join(_icons, 'bookmarks.png'),
                'icon': os.path.join(_icons, 'bookmarks.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='my_shows'),
                }]
    return listing


@plugin.cached(15)
def episode_list(params):
    """
    The list of recent episodes
    :param params:
    :return:
    """
    listing = [_home]
    episodes = parser.load_episodes(params['page'], params.get('query', ''), params.get('imdb', ''))  # Get episodes
    if episodes['episodes']:
        if episodes['prev']:
            prev_item = {'label': '{0} < Previous'.format(episodes['prev']),
                         'thumb': os.path.join(_icons, 'previous.png'),
                         'icon': os.path.join(_icons, 'previous.png'),
                         'fanart': plugin.fanart}
            if params.get('imdb') is not None:
                prev_item['url'] = plugin.get_url(action='episode_list',
                                                   imbd=params['imdb'],
                                                   page=episodes['prev'])
            else:
                prev_item['url'] = plugin.get_url(action='episode_list', page=episodes['prev'])
                if params.get('query') is not None:
                    prev_item['url'] += '&query=' + params['query']
            listing.append(prev_item)
        for episode in episodes['episodes']:
            if int(episode['seeders']) <= 10:
                if plugin.get_setting('ignore_weak'):
                    continue
                episode['seeders'] = '[COLOR=red]{0}[/COLOR]'.format(episode['seeders'])
            elif int(episode['seeders']) <= 25:
                episode['seeders'] = '[COLOR=yellow]{0}[/COLOR]'.format(episode['seeders'])
            thumb = episode['thumb'] if episode['thumb'] else os.path.join(_icons, 'tv.png')
            listing.append({'label': '{0} [COLOR=gray]({1}|S:{2}/L:{3})[/COLOR]'.format(episode['title'],
                                                                                        episode['size'],
                                                                                        episode['seeders'],
                                                                                        episode['leechers']),
                            'thumb': thumb,
                            'icon': thumb,
                            'fanart': plugin.fanart,
                            'info': {'video': episode['info']},
                            'url': plugin.get_url(action='episode', url=urlsafe_b64encode(episode['link'])),
                            })
        if episodes['next']:
            next_item = {'label': 'Next > {0}'.format(episodes['next']),
                         'thumb': os.path.join(_icons, 'next.png'),
                         'icon': os.path.join(_icons, 'next.png'),
                         'fanart': plugin.fanart}
            if params.get('imdb') is not None:
                next_item['url'] = plugin.get_url(action='episode_list',
                                                   imbd=params['imdb'],
                                                   page=episodes['next'])
            else:
                next_item['url'] = plugin.get_url(action='episode_list', page=episodes['next'])
                if params.get('query') is not None:
                    next_item['url'] += '&query=' + params['query']
            listing.append(next_item)
    else:
        xbmcgui.Dialog().notification('Error!', 'No episodes to dislpay!', 'error', 3000)
        plugin.log('Empty episode list returned.', xbmc.LOGERROR)
    return listing


def search_episodes(params):
    """
    Search episodes
    :param params:
    :return:
    """
    keyboard = xbmc.Keyboard('', 'Enter a search query')
    keyboard.doModal()
    query_text = keyboard.getText()
    if keyboard.isConfirmed():
        query = quote_plus(query_text)
        plugin.log('Search query: {0}'.format(query))
        params['query'] = query
        return episode_list(params)
    else:
        xbmcgui.Dialog().notification(plugin.id, 'Search cancelled!', plugin.icon, 3000)
        return [_home]


@plugin.cached(60)
def episode(params):
    """
    Show episode info
    :param params:
    :return:
    """
    listing = []
    episode_data = parser.load_episode_page(urlsafe_b64decode(params['url']))
    if episode_data['filename']:
        try:
            if int(episode_data['seeders']) <= 10:
                episode_data['seeders'] = '[COLOR=red]{0}[/COLOR]'.format(episode_data['seeders'])
            elif int(episode_data['seeders']) <= 25:
                episode_data['seeders'] = '[COLOR=yellow]{0}[/COLOR]'.format(episode_data['seeders'])
        except ValueError:
            pass
        poster = episode_data['poster'] if episode_data['poster'] else os.path.join(_icons, 'tv.png')
        episode = {'label': '{0} [COLOR=gray]({1}|S:{2}/L:{3})[/COLOR]'.format(episode_data['filename'],
                                                                               episode_data['size'],
                                                                               episode_data['seeders'],
                                                                               episode_data['leechers']),
                   'thumb': poster,
                   'icon': poster,
                   'fanart': plugin.fanart,
                   'info': {'video': episode_data['info']},
                   'context_menu': [('Add to "My Shows"',
                                     'RunScript({0}/libs/commands.py,myshows_add,{1},{2},{3},{4})'.format(
                                         plugin.path,
                                         plugin.config_dir,
                                         episode_data['info']['title'],
                                         episode_data['imdb'],
                                         episode_data['poster'])),
                                    ('Download torrent...',
                                     'RunScript({0}/libs/commands.py,download,{1})'.format(
                                         plugin.path,
                                         episode_data['torrent'])),
                                    ],
                   'url': plugin.get_url('plugin://plugin.video.yatp/',
                                          action='play',
                                          torrent=urlsafe_b64encode(episode_data['torrent']),
                                          title=urlsafe_b64encode(episode_data['info']['title']),
                                          thumb=urlsafe_b64encode(poster)),
                   'is_folder': False,
                   }
        try:
            episode['url'] += '&season={0}'.format(episode_data['info']['season'])
            episode['url'] += '&episode={0}'.format(episode_data['info']['episode'])
        except KeyError:
            pass
        episode['stream_info'] = {}
        if episode_data.get('video') is not None:
            episode['stream_info']['video'] = episode_data['video']
        if episode_data.get('audio') is not None:
            episode['stream_info']['audio'] = episode_data['audio']
        if episode_data.get('subtitle') is not None:
            episode['stream_info']['subtitle'] = episode_data['subtitle']
        listing.append(episode)
    else:
        xbmcgui.Dialog().notification('Error!', 'No episode data to dislpay!', 'error', 3000)
        plugin.log('Empty episode data returned.', xbmc.LOGERROR)
    return listing


def my_shows(params):
    """
    "My Shows" - the list of favorite TV shows.
    :param params:
    :return:
    """
    listing = [_home]
    with plugin.get_storage('myshows.pcl') as storage:
        myshows = storage.get('myshows', [])
        for index, show in enumerate(myshows):
            listing.append({'label': show[0],
                            'thumb': show[2],
                            'icon': show[2],
                            'fanart': plugin.fanart,
                            'url': plugin.get_url(action='episode_list', page='1', imdb=show[1]),
                            'context_menu': [('Remove from "My Shows"',
                                              'RunScript({0}/libs/commands.py,myshows_remove,{1},{2})'.format(
                                                  plugin.path,
                                                  plugin.config_dir,
                                                  index))],
                            })
    return listing


# Map actions
plugin.actions['root'] = root
plugin.actions['episode_list'] = episode_list
plugin.actions['search_episodes'] = search_episodes
plugin.actions['episode'] = episode
plugin.actions['my_shows'] = my_shows
