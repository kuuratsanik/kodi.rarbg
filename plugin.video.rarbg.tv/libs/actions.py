# -*- coding: utf-8 -*-
# Module: actions
# Author: Roman V.M.
# Created on: 09.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Plugin actions"""

import os
import re
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from simpleplugin import Plugin
import torrent_info
import tvdb

__all__ = ['plugin']

plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
tv_icon = os.path.join(icons, 'tv.png')
home = {'label': '<< Home',
        'thumb': os.path.join(icons, 'home.png'),
        'icon': os.path.join(icons, 'home.png'),
        'art': {'poster': os.path.join(icons, 'home.png')},
        'fanart': plugin.fanart,
        'url': plugin.get_url(),
        'info': {'video': {'title': '<< Home'}}}
commands = os.path.join(plugin.path, 'libs', 'commands.py')


@plugin.cached(15)
def _get_torrents(mode, category='', search_string='', search_imdb=''):
    """
    Get torrents from Rarbg.to

    :param mode: Rarbg query mode -- 'list' or 'search'
    :type mode: str
    :param category: Rarbg torrents category
    :type category: str
    :param search_string: search query
    :type search_string: str
    :param search_imdb: imdb code for a TV show as ttXXXXX
    :type search_imdb: str
    :return: the list of torrents matching the query criteria
    :rtype: list
    """
    rarbg_query = {'mode': mode, 'limit': plugin.itemcount}
    if plugin.get_setting('ignore_weak'):
        rarbg_query['min_seeders'] = plugin.get_setting('min_seeders', False)
    if category:
        rarbg_query['category'] = category
    if search_string:
        rarbg_query['search_string'] = search_string
    if search_imdb:
        rarbg_query['search_imdb'] = search_imdb
    return torrent_info.get_torrents(rarbg_query)


def _set_view_mode(content=''):
    """
    Set view mode

    :param content: view content type: 'icons' -- icons view, 'episodes' -- episodes view,
        '' -- generic Kodi list view
    :type content: str
    :return: Numeric view code for the current skin, if supported, or 50 for generic list view.
    :rtype: int
    """
    view_mode = 50
    if content:
        if xbmc.getSkinDir() == 'skin.confluence':
            if content == 'icons':
                view_mode = 500
            else:
                view_mode = 503
        elif xbmc.getSkinDir() == 'skin.re-touched':
            if content == 'episodes':
                view_mode = 550
            else:
                view_mode = 500
    return view_mode


def _get_category():
    """
    Get Rarbg torrents category

    :return: Rarbg torrnts cagegory for SD episodes/HD episodes/both
    :rtype: str
    """
    return ('18;41', '18', '41',)[plugin.quality]


def _set_info(list_item, torrent, myshows=False):
    """
    Set show and episode info for a list_item

    :param list_item: SimplePlugin list item to be updated
    :type list_item: dict
    :param torrent: torrent data
    :type torrent: dict
    :param myshows: ``True`` if the item is displayed in "My Shows"
    :type myshows: bool
    """
    video = {}
    if torrent.get('episode_info'):
        video['season'] = int(torrent['episode_info']['seasonnum'])
        video['episode'] = int(torrent['episode_info']['epnum'])
    if torrent.get('show_info') is not None:
        video['genre'] = torrent['show_info'].get('Genre', '').lstrip('|').rstrip('|').replace('|', ', ')
        video['cast'] = torrent['show_info'].get('Actors', '').lstrip('|').rstrip('|').split('|')
        video['mpaa'] = torrent['show_info'].get('ContentRating', '')
        video['tvshowtitle'] = list_item['label2'] = torrent['show_info'].get('SeriesName', '')
        video['plot'] = video['plotoutline'] = torrent['show_info'].get('Overview', '')
        video['studio'] = torrent['show_info'].get('Network', '')
        if torrent['show_info'].get('FirstAired'):
            video['year'] = int(torrent['show_info']['FirstAired'][:4])
    if torrent.get('tvdb_episode_info') is not None:
        video['director'] = torrent['tvdb_episode_info'].get('Director', '',)
        video['credits'] = torrent['tvdb_episode_info'].get('Writer', '').lstrip('|').rstrip('|').replace('|', ', ')
        video['premiered'] = (torrent['tvdb_episode_info'].get('FirstAired', '') or
                              torrent['episode_info'].get('airdate', ''))
        if torrent['tvdb_episode_info'].get('Rating'):
            video['rating'] = float(torrent['tvdb_episode_info']['Rating'])
        if myshows:
            video['plot'] = video['plotoutline'] = torrent['tvdb_episode_info'].get('Overview', '')
            list_item['label'] = (torrent['tvdb_episode_info'].get('EpisodeName') or
                                  torrent['episode_info'].get('title') or
                                  torrent['title'])
    video['title'] = list_item['label']
    list_item['info'] = {'video': video}


def _set_art(list_item, torrent, myshows=False):
    """
    Set graphics for a list_item

    :param list_item: SimplePlugin list item to be updated
    :type list_item: dict
    :param torrent: torrent data
    :type torrent: dict
    :param myshows: ``True`` if the item is displayed in "My Shows"
    :type myshows: bool
    """
    if torrent['show_info'] is not None:
        if torrent['tvdb_episode_info'] is not None and myshows:
            list_item['thumb'] = list_item['icon'] = (torrent['tvdb_episode_info'].get('filename', '') or
                                                      torrent['show_info'].get('poster', ''))
        else:
            list_item['thumb'] = list_item['icon'] = torrent['show_info'].get('poster', '')
        list_item['fanart'] = torrent['show_info'].get('fanart', plugin.fanart)
        list_item['art'] = {'poster': torrent['show_info'].get('poster', ''),
                            'banner': torrent['show_info'].get('banner', '')}
    else:
        list_item['thumb'] = list_item['icon'] = tv_icon
        list_item['fanart'] = plugin.fanart


def _set_stream_info(list_item, torrent):
    """
    Set additional video stream info.

    :param list_item: SimplePlugin list item to be updated
    :type list_item: dict
    :param torrent: torrent data
    :type torrent: dict
    """
    video = {}
    resolution_match = re.search(r'(720|1080)[pi]', torrent['title'], flags=re.IGNORECASE)
    if resolution_match is not None and resolution_match.group(1) == '720':
        video['width'] = 1280
        video['height'] = 720
    elif resolution_match is not None and resolution_match.group(1) == '1080':
        video['width'] = 1920
        video['height'] = 1080
    else:
        video['width'] = 720
        video['height'] = 480
    codec_match = re.search(r'[hx]\.?264|xvid|divx|mpeg2', torrent['title'], flags=re.IGNORECASE)
    if codec_match is not None:
        if codec_match.group(0).endswith('264'):
            video['codec'] = 'h264'
        elif codec_match.group(0) == 'mpeg2':
            video['codec'] = 'mpeg2video'
        else:
            video['codec'] = codec_match.group(0)
    list_item['stream_info'] = {'video': video}


def _enter_search_query():
    """
    Enter a search query on Kodi on-screen keyboard.

    :return:
    """
    keyboard = xbmc.Keyboard('', 'Enter search text')
    keyboard.doModal()
    text = keyboard.getText()
    if keyboard.isConfirmed() and text:
        query = urllib.quote_plus(text)
    else:
        query = ''
    return query


def _list_torrents(torrents, myshows=False):
    """
    Show the list of torrents

    :param torrents: list
    :return:
    """
    listing = [home]
    for torrent in torrents:
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
                     'url': plugin.get_url(action='play', torrent=torrent['download']),
                     'is_playable': True,
                     'context_menu': [('Show info', 'Action(Info)'),
                                      ('Mark as watched/unwatched', 'Action(ToggleWatched)'),
                                      ('Download torrent',
                                       'RunScript({commands},download,{torrent})'.format(
                                            commands=commands,
                                            torrent=torrent['download'])
                                       )]
                     }
        _set_info(list_item, torrent, myshows)
        _set_art(list_item, torrent, myshows)
        _set_stream_info(list_item, torrent)
        if myshows:
            list_item['context_menu'].append(
                ('Torrent info',
                 'RunScript({commands},torrent_info,{title},{size},{seeders},{leechers})'.format(
                    commands=commands,
                    title=torrent['title'],
                    size=torrent['size'] / 1048576,
                    seeders=torrent['seeders'],
                    leechers=torrent['leechers'])))
        else:
            list_item['context_menu'].append(('Add to "My shows"...',
                                              'RunScript({commands},myshows_add,{config_dir},{tvdb})'.format(
                                                  commands=commands,
                                                  config_dir=plugin.config_dir,
                                                  tvdb=torrent['episode_info']['tvdb'])))
        listing.append(list_item)
    return listing


def root(params):
    """
    Plugin root

    :param params:
    :return:
    """
    listing = [{'label': '[My shows]',
                'thumb': os.path.join(icons, 'bookmarks.png'),
                'icon': os.path.join(icons, 'bookmarks.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='my_shows'),
               },
               {'label': '[Recent Episodes]',
                'thumb': os.path.join(icons, 'tv.png'),
                'icon': tv_icon,
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='episodes', mode='list'),
                },
               {'label': '[Search TV torrents...]',
                'thumb': os.path.join(icons, 'search.png'),
                'icon': os.path.join(icons, 'search.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='search_torrents')
               }]
    return plugin.create_listing(listing, view_mode=_set_view_mode('icons'))


def episodes(params):
    """
    Show the list of recent episodes

    :param params:
    :return:
    """
    myshows = params.get('myshows', False)
    listing = _list_torrents(_get_torrents(params['mode'],
                                           search_imdb=params.get('search_imdb', ''),
                                           category=_get_category()),
                             myshows=myshows)
    if myshows:
        content = 'episodes'
        sort_methods = (xbmcplugin.SORT_METHOD_EPISODE,)
    else:
        content = ''
        sort_methods = ()
    return plugin.create_listing(listing, content=content, view_mode=_set_view_mode(content), sort_methods=sort_methods)


def search_torrents(params):
    """
    Search torrents and show the list of results

    :param params:
    :return:
    """
    results = []
    query = _enter_search_query()
    if query:
        results = _get_torrents(mode='search',
                                search_string=query,
                                category=_get_category())
        if not results:
            xbmcgui.Dialog().ok('Nothing found!', 'Adjust your search string and try again.')
    listing = _list_torrents(results)
    return plugin.create_listing(listing, cache_to_disk=True)


def my_shows(params):
    """
    'My Shows' list

    :param params: SimplePlugin action call params
    :type params: dict
    :return: SimplePlugin action context
    :rtype: dict
    """
    listing = [home]
    with plugin.get_storage('myshows.pcl') as storage:
        myshows = storage.get('myshows', [])
    with plugin.get_storage('tvshows.pcl') as tvshows:
        for index, show in enumerate(myshows):
            if show not in tvshows:
                tvshows[show] = tvdb.get_series(show)
            list_item = {'label': tvshows[show]['SeriesName'],
                         'url': plugin.get_url(action='episodes',
                                               mode='search',
                                               search_imdb=tvshows[show]['IMDB_ID'],
                                               myshows='true'),
                         'context_menu': [('Show info', 'Action(Info)'),
                                          ('Remove from "My Shows"...',
                                           'RunScript({commands},myshows_remove,{config_dir},{index})'.format(
                                               commands=commands,
                                               config_dir=plugin.config_dir,
                                               index=index))]}
            _set_info(list_item, {'show_info': tvshows[show], 'tvdb_episode_info': None})
            _set_art(list_item, {'show_info': tvshows[show], 'tvdb_episode_info': None})
            listing.append(list_item)
    content = 'tvshows'
    return plugin.create_listing(listing, view_mode=_set_view_mode(content), content=content,
                                 sort_methods=(xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE,))


def play(params):
    """
    Play torrent via YATP

    :param params:
    :return:
    """
    return plugin.get_url('plugin://plugin.video.yatp/', action='play', torrent=params['torrent'])

# Map actions
plugin.actions['root'] = root
plugin.actions['episodes'] = episodes
plugin.actions['search_torrents'] = search_torrents
plugin.actions['my_shows'] = my_shows
plugin.actions['play'] = play
