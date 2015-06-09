# -*- coding: utf-8 -*-
# Module: actions
# Author: Roman V.M.
# Created on: 09.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
from base64 import urlsafe_b64encode
from simpleplugin import Plugin
import parser

_plugin = Plugin()
_icons = os.path.join(_plugin.path, 'resources', 'icons')


@_plugin.cached(60)
def root(params):
    """
    Plugin root
    :param params:
    :return:
    """
    listing = [{'label': '[Recent Episodes]',
                'thumb': os.path.join(_icons, 'tv.png'),
                'icon': os.path.join(_icons, 'tv.png'),
                'fanart': _plugin.fanart,
                'url': _plugin.get_url(action='episode_list', page='1'),
                },
               {'label': '[Search episodes...]',
                'thumb': os.path.join(_icons, 'search.png'),
                'icon': os.path.join(_icons, 'search.png'),
                'fanart': _plugin.fanart,
                'url': _plugin.get_url(action='search_episode', page='1'),
                },
               {'label': '[My Shows]',
                'thumb': os.path.join(_icons, 'bookmarks.png'),
                'icon': os.path.join(_icons, 'bookmarks.png'),
                'fanart': _plugin.fanart,
                'url': _plugin.get_url(action='my_shows'),
                }]
    return listing


@_plugin.cached(15)
def episode_list(params):
    """
    The list of recent episodes
    :param params:
    :return:
    """
    listing = [{'label': '<< Home',
                'thumb': os.path.join(_icons, 'home.png'),
                'icon': os.path.join(_icons, 'home.png'),
                'fanart': _plugin.fanart,
                'url': _plugin.get_url()
                }]
    episodes = parser.load_episodes(params['page'], params.get('query', ''), params.get('imdb', ''))  # Get episodes
    if episodes['episodes']:
        if episodes['prev']:
            prev_item = {'label': '{0} < Previous'.format(episodes['prev']),
                         'thumb': os.path.join(_icons, 'previous.png'),
                         'icon': os.path.join(_icons, 'previous.png'),
                         'fanart': _plugin.fanart}
            if params.get('query') is not None:
                prev_item['url'] = _plugin.get_url(action='search_episodes',
                                                   query=params['query'],
                                                   page=episodes['prev'])
            elif params.get('imdb') is not None:
                prev_item['url'] = _plugin.get_url(action='episode_list',
                                                   imbd=params['imdb'],
                                                   page=episodes['prev'])
            else:
                prev_item['url'] = _plugin.get_url(action='episode_list', page=episodes['prev'])
            listing.append(prev_item)
        for episode in episodes:
            if int(episode['seeders']) <= 10:
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
                            'fanart': _plugin.fanart,
                            'info': {'video': episode['info']},
                            'url': _plugin.get_url(action=episode, url=urlsafe_b64encode(episode['link'])),
                            })
        if episodes['next']:
            next_item = {'label': 'Next > {0}'.format(episodes['next']),
                         'thumb': os.path.join(_icons, 'next.png'),
                         'icon': os.path.join(_icons, 'next.png'),
                         'fanart': _plugin.fanart}
            if params.get('query') is not None:
                next_item['url'] = _plugin.get_url(action='search_episodes',
                                                   query=params['query'],
                                                   page=episodes['next'])
            elif params.get('imdb') is not None:
                next_item['url'] = _plugin.get_url(action='episode_list',
                                                   imbd=params['imdb'],
                                                   page=episodes['next'])
            else:
                next_item['url'] = _plugin.get_url(action='episode_list', page=episodes['next'])
            listing.append(next_item)
    return listing
