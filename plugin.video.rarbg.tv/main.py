# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from simpleplugin import Plugin
from libs import actions

plugin = Plugin()
plugin.actions['root'] = actions.root
plugin.actions['episode_list'] = actions.episode_list

if __name__ == '__main__':
    plugin.run(content='tvshows')


'''

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
        keyboard = xbmc.Keyboard('', 'Enter a search query')
        keyboard.doModal()
        query_text = keyboard.getText()
        if keyboard.isConfirmed() and query_text:
            views.episode_list_view(__url__, __handle__, '1', search_query=quote_plus(query_text))
        else:
            xbmcgui.Dialog().notification('Note!', 'Search cancelled', __addon__.icon, 3000)
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
            episode_list(params['page'], params.get('imdb', ''))
        elif params['action'] == 'episode':
            episode_page(params['url'])
        elif params['action'] == 'search_episodes':
            search_episodes(params['page'], params.get('query', ''))
        elif params['action'] == 'my_shows':
            my_shows()
        else:
            raise RuntimeError('Invalid action: {0}'.format(params['action']))
    else:
        plugin_root()


'''
