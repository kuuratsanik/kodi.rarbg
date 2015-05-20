# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from base64 import urlsafe_b64decode
from urlparse import parse_qsl
from urllib import quote_plus
# Kodi modules
import xbmcplugin
import xbmc
import xbmcgui
# Custom modules
from libs import views
from libs.addon import Addon


__addon__ = Addon()
__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
xbmcplugin.setContent(__handle__, 'tvshows')


def plugin_root():
    """
    Plugin root
    :return:
    """
    views.root_view(__url__, __handle__)


def episode_list(page, imdb):
    """
    The list of episode releases by most recent first
    :param page: str - page#
    :param imdb: str - IMDB ID (tt123456)
    :return:
    """
    views.episode_list_view(__url__, __handle__, page, imdb=imdb)


def episode_page(encoded_url):
    """
    Episode page
    :param encoded_url: str - episode page URL in base64 encoding
    :return:
    """
    views.episode_view(__handle__, urlsafe_b64decode(encoded_url))


def search_episodes(page, query):
    """
    Search episodes
    :param page: str - page #
    :param query: str - search query
    :return:
    """
    if not query:
        keyboard = xbmc.Keyboard('Enter search query')
        keyboard.doModal()
        query_text = keyboard.getText()
        if keyboard.isConfirmed() and query_text:
            views.episode_list_view(__url__, __handle__, '1', search_query=quote_plus(query_text))
        else:
            xbmcgui.Dialog().notification('Note!', 'Search cancelled', 'info', 3000)
            xbmcplugin.endOfDirectory(__handle__, False)
    else:
        views.episode_list_view(__url__, __handle__, page, search_query=query)


def my_shows():
    """
    The list of favorite shows
    :return:
    """
    views.my_shows_view(__url__, __handle__)


def router(paramstring):
    """
    Plugin router function
    :param paramstring: str - URL-encoded addon call paramstring
    :return:
    """
    params = dict(parse_qsl(paramstring[1:]))
    if params:
        if params['action'] == 'episode_list':
            try:
                imdb = params['imdb']
            except KeyError:
                imdb = ''
            episode_list(params['page'], imdb)
        elif params['action'] == 'episode':
            episode_page(params['url'])
        elif params['action'] == 'search_episodes':
            try:
                query = params['query']
            except KeyError:
                query = ''
            search_episodes(params['page'], query)
        elif params['action'] == 'my_shows':
            my_shows()
        else:
            raise RuntimeError('Invalid action: {0}'.format(params['action']))
    else:
        plugin_root()


if __name__ == '__main__':
    __addon__.log(str(sys.argv))
    router(sys.argv[2])
