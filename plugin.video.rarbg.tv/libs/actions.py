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
import thetvdb

plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
home = {'label': '<< Home',
         'thumb': os.path.join(icons, 'home.png'),
         'icon': os.path.join(icons, 'home.png'),
         'art': {'poster': os.path.join(icons, 'home.png')},
         'fanart': plugin.fanart,
         'url': plugin.get_url(),
         'info': {'video': {'title': '<< Home'}}}
commands = os.path.join(plugin.path, 'libs', 'commands.py')


@plugin.cached(15)
def _get_torrents(mode, category='', search_sthring='', search_imdb=''):
    """
    Get torrents from Rarbg.to

    @param mode:
    @param category:
    @param search_sthring:
    @param search_imdb:
    @return:
    """
    rarbg_params = {'mode': mode, 'limit': plugin.get_setting('itemcount')}
    if plugin.get_setting('ignore_weak'):
        rarbg_params['min_seeders'] = plugin.get_setting('min_seeders', False)
    if category:
        rarbg_params['category'] = category
    if search_sthring:
        rarbg_params['search_string'] = search_sthring
    if search_imdb:
        rarbg_params['search_imdb'] = search_imdb
    return torrent_info.get_torrents(rarbg_params)


def _set_view_mode():
    """
    Set view mode

    @return:
    """
    if xbmc.getSkinDir() == 'skin.confluence':
        view_mode = 503
    else:
        view_mode = 50
    return view_mode


def _get_category():
    """
    Get Rarbg torrents category

    @return:
    """
    return ('18;41', '18', '41',)[plugin.get_setting('quality')]


def _set_info(list_item, torrent, myshows=False):
    """
    Set info for list_item

    @param torrent:
    @return:
    """
    video = {'genre': torrent['show_info'].get('Genre', '').lstrip('|').rstrip('|').replace('|', ', '),
             'cast': torrent['show_info'].get('Actors', '').lstrip('|').rstrip('|').split('|'),
             'mpaa': torrent['show_info'].get('ContentRating', ''),
             'tvshowtitle': torrent['show_info'].get('SeriesName', ''),
             'plot': torrent['show_info'].get('Overview', ''),
             'plotoutline': torrent['show_info'].get('Overview', ''),
             'studio': torrent['show_info'].get('Network', '')}
    title = list_item['label']
    if torrent['tvdb_episode_info'] == {}:
        title = torrent['show_info'].get('SeriesName', '')
        video['premiered'] = torrent['show_info'].get('FirstAired', '')
    else:
        video['season'] = int(torrent['episode_info']['seasonnum'])
        video['episode'] = int(torrent['episode_info']['epnum'])
        if torrent['tvdb_episode_info']:
            video['director'] = torrent['tvdb_episode_info'].get('Director', '',)
            video['premiered'] = torrent['tvdb_episode_info'].get('FirstAired', '')
            video['credits'] = torrent['tvdb_episode_info'].get('Writer', '')
            video['premiered'] = (torrent['tvdb_episode_info'].get('FirstAired', '') or
                                  torrent['episode_info'].get('airdate', ''))
            if torrent['tvdb_episode_info'].get('Rating'):
                video['rating'] = float(torrent['tvdb_episode_info']['Rating'])
            if myshows:
                video['plot'] = video['plotoutline'] = torrent['tvdb_episode_info'].get('Overview', '')
                list_item['label'] = title = (torrent['tvdb_episode_info'].get('EpisodeName') or
                                              torrent['episode_info']['title'])
    video['title'] = title
    if torrent['show_info'].get('FirstAired'):
        video['year'] = int(torrent['show_info']['FirstAired'][:4])
    list_item['info'] = {}
    list_item['info']['video'] = video


def _set_art(list_item, torrent, myshows=False):
    """
    Set graphics for list_item

    @param list_item:
    @param torrent:
    @param myshows:
    @return:
    """
    if torrent['tvdb_episode_info'] and myshows:
        list_item['thumb'] = list_item['icon'] = (torrent['tvdb_episode_info'].get('filename', '') or
                                                  torrent['show_info'].get('poster', ''))
    else:
        list_item['thumb'] = list_item['icon'] = torrent['show_info'].get('poster', '')
    list_item['fanart'] = torrent['show_info'].get('fanart', plugin.fanart)
    list_item['art'] = {'poster': torrent['show_info'].get('poster', ''),
                        'banner': torrent['show_info'].get('banner', '')}


def _set_stream_info(list_item, torrent):
    """
    Set additional video stream info.

    @param list_item:
    @param torrent:
    @return:
    """
    list_item['stream_info'] = {'video': {}}
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
    codec_match = re.search(r'[hx]\.?264|xvid|divx|mpeg2', torrent['title'].lower())
    if codec_match is not None:
        if codec_match.group(0).endswith('264'):
            list_item['stream_info']['video']['codec'] = 'h264'
        elif codec_match.group(0) == 'mpeg2':
            list_item['stream_info']['video']['codec'] = 'mpeg2video'
        else:
            list_item['stream_info']['video']['codec'] = codec_match.group(0)


def _enter_search_query():
    """
    Enter a search query on Kodi on-screen keyboard.

    @return:
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

    @param torrents: list
    @return:
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
                     'context_menu': [('Mark as watched/unwatched', 'Action(ToggleWatched)')]
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
            list_item['context_menu'].append(
                ('Add to "My shows"...',
                 'RunScript({commands},myshows_add,{config_dir},{imdb})'.format(
                    commands=commands,
                    config_dir=plugin.config_dir,
                    imdb=torrent['episode_info']['imdb'])))
        if plugin.get_setting('stream_engine') == 'YATP':
            list_item['context_menu'].append(
                ('Download torrent',
                 'RunScript({commands},download,{torrent})'.format(
                    commands=commands,
                    torrent=torrent['download'])
                 ))
        listing.append(list_item)
    return plugin.create_listing(listing, content='episodes', view_mode=_set_view_mode())


def root(params):
    """
    Plugin root

    @param params:
    @return:
    """
    listing = [{'label': '[My shows]',
                'thumb': os.path.join(icons, 'bookmarks.png'),
                'icon': os.path.join(icons, 'bookmarks.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='my_shows'),
               },
               {'label': '[Recent Episodes]',
                'thumb': os.path.join(icons, 'tv.png'),
                'icon': os.path.join(icons, 'tv.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='episodes', mode='list'),
                },
               {'label': '[Search TV torrents...]',
                'thumb': os.path.join(icons, 'search.png'),
                'icon': os.path.join(icons, 'search.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='search_torrents')
               }]
    return listing


def episodes(params):
    """
    Show the list of recent episodes

    @param params:
    @return:
    """
    return _list_torrents(_get_torrents(params['mode'],
                                        search_imdb=params.get('search_imdb', ''),
                                        category=_get_category()),
                          myshows=params.get('myshows', False))


def search_torrents(params):
    """
    Search torrents and show the list of results

    @param params:
    @return:
    """
    results = []
    query = _enter_search_query()
    if query:
        results = _get_torrents(mode='search',
                                search_sthring=query,
                                category=_get_category())
        if not results:
            xbmcgui.Dialog().ok('Nothing found!', 'Adjust your search string and try again.')
    context = _list_torrents(results)
    context['cache_to_disk'] = True
    return context


def my_shows(params):
    """
    'My Shows' list

    @param params:
    @return:
    """
    listing = [home]
    with plugin.get_storage('myshows.pcl') as storage:
        myshows = storage.get('myshows', [])
    with plugin.get_storage('tvshows.pcl') as tvshows:
        for index, show in enumerate(myshows):
            list_item = {'label': tvshows[show]['SeriesName'],
                         'url': plugin.get_url(action='episodes',
                                               mode='search',
                                               search_imdb=show,
                                               myshows='true'),
                         'context_menu': [('Remove from "My Shows"...',
                            'RunScript({commands},myshows_remove,{config_dir},{index})'.format(
                             commands=commands,
                             config_dir=plugin.config_dir,
                             index=index
                         ))]}
            if not tvshows.get(show):
                tvshows[show] = thetvdb.get_series(thetvdb.get_series_by_imdbid(show)['seriesid'])
            _set_info(list_item, {'show_info': tvshows[show], 'tvdb_episode_info': {}})
            _set_art(list_item, {'show_info': tvshows[show], 'tvdb_episode_info': {}})
            listing.append(list_item)
    return plugin.create_listing(listing, view_mode=_set_view_mode(), content='tvshows',
                                 sort_methods=(xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE,))


def search_thetvdb(params):
    """
    Serch a show on TheTVDB

    @param params:
    @return:
    """
    query = _enter_search_query()
    if query:
        tvshows = thetvdb.search_series(query)
        if tvshows:
            index = xbmcgui.Dialog().select('Select a TV show', [show['tvshowtitle'] for show in tvshows])
            if index >= 0:
                return episodes({'mode': 'search', 'search_imdb': tvshows[index]['imdb']})
        else:
            xbmcgui.Dialog().ok('Nothing found!', 'Adjust your search string and try again.')
    return plugin.create_listing([home], view_mode=_set_view_mode())


def play(params):
    """
    Play torrent via YATP of Pulsar

    @param params:
    @return:
    """
    if plugin.get_setting('stream_engine') == 'YATP':
        return plugin.get_url('plugin://plugin.video.yatp/', action='play', torrent=params['torrent'])
    else:
        return plugin.get_url('plugin://plugin.video.pulsar/play', uri=params['torrent'])


# Map actions
plugin.actions['root'] = root
plugin.actions['episodes'] = episodes
plugin.actions['search_torrents'] = search_torrents
plugin.actions['my_shows'] = my_shows
plugin.actions['search_thetvdb'] = search_thetvdb
plugin.actions['play'] = play
