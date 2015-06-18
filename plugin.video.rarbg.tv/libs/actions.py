# -*- coding: utf-8 -*-
# Module: actions
# Author: Roman V.M.
# Created on: 09.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
from simpleplugin import Plugin

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



# Map actions
plugin.actions['root'] = root
