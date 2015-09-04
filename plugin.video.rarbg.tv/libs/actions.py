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
_icons = os.path.join(plugin.path, 'resources', 'icons')
_home = {'label': '<< Home',
         'thumb': os.path.join(_icons, 'home.png'),
         'icon': os.path.join(_icons, 'home.png'),
         'art': {'poster': os.path.join(_icons, 'home.png')},
         'fanart': plugin.fanart,
         'url': plugin.get_url(),
         'info': {'video': {'title': '<< Home'}}}


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


def _set_info(list_item, torrent, myshows):
    """
    Set additional info

    @param torrent:
    @return:
    """
    video = {'title': torrent['episode_info']['episode_name'] if myshows else list_item['label']}
    if torrent['show_info'] is not None:
        video['tvshowtitle'] = torrent['show_info']['tvshowtitle']
        if myshows and torrent['episode_info'].get('plot'):
            video['plot'] = torrent['episode_info']['plot']
        else:
            video['plot'] = torrent['show_info']['plot']
        video['genre'] = torrent['show_info']['genre']
        video['year'] = int(torrent['show_info']['premiered'][:4])
        video['season'] = 0  # Needed for Kodi to treat the item as an episode
        if myshows and torrent['episode_info'].get('thumb'):
            list_item['thumb'] = list_item['icon'] = torrent['episode_info']['thumb']
        else:
            list_item['thumb'] = list_item['icon'] = torrent['show_info']['poster']
        list_item['art'] = {'poster': torrent['show_info']['poster']}
        if torrent['show_info']['banner'] is not None:
            list_item['art']['banner'] = torrent['show_info']['banner']
        if torrent['show_info'].get('clearlogo'):
            list_item['art']['clearlogo'] = torrent['show_info']['clearlogo']
        if torrent['show_info'].get('clearart'):
            list_item['art']['clearart'] = torrent['show_info']['clearart']
        if torrent['show_info'].get('landscape'):
            list_item['art']['landscape'] = torrent['show_info']['landscape']
        list_item['fanart'] = torrent['show_info'].get('fanart', plugin.fanart)
    else:
        list_item['thumb'] = list_item['icon'] = os.path.join(_icons, 'tv.png')
        list_item['fanart'] = plugin.fanart
    if torrent['episode_info'].get('epnum') is not None:
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
    list_item['info'] = {}
    list_item['info']['video'] = video


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

    @param torrents:
    @type torrents: list
    @return:
    """
    listing = [_home]
    for index, torrent in enumerate(torrents):
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
                     'is_playable': True,
                     'url': plugin.get_url(action='play', torrent=torrent['download']),
                     'context_menu': [('Mark as watched/unwatched', 'Action(ToggleWatched)')]
                     }
        _set_info(list_item, torrent, myshows)
        _set_stream_info(list_item, torrent)
        if not myshows and torrent['show_info']:
            list_item['context_menu'].append(
                ('Add to "My shows"...',
    u'RunScript({plugin_path}/libs/commands.py,myshows_add,{config_dir},{title},{thumb},{imdb})'.format(
                    plugin_path=plugin.path,
                    config_dir=plugin.config_dir,
                    title=torrent['show_info']['tvshowtitle'],
                    thumb=torrent['show_info']['poster'],
                    imdb=torrent['episode_info']['imdb'])))
        # plugin.log(str(list_item))
        listing.append(list_item)
    sort_methods = (xbmcplugin.SORT_METHOD_EPISODE,) if myshows else None
    return plugin.create_listing(listing, content='episodes', view_mode=_set_view_mode(), sort_methods=sort_methods)


def root(params):
    """
    Plugin root

    @param params:
    @return:
    """
    listing = [{'label': '[Recent Episodes]',
                'thumb': os.path.join(_icons, 'tv.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='episodes', mode='list'),
                },
               {'label': '[My shows]',
                'thumb': os.path.join(_icons, 'bookmarks.png'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='my_shows'),
               },
               {'label': '[Search Rarbg TV torrents...]',
                'thumb': plugin.icon,
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='search_torrents')
               },
               {'label': '[Search using TheTVDB...]',
                'thumb': os.path.join(_icons, 'thetvdb.jpg'),
                'fanart': plugin.fanart,
                'url': plugin.get_url(action='search_thetvdb')
                }
               ]
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
    return _list_torrents(results)


def my_shows(params):
    """
    'My Shows' list

    @param params:
    @return:
    """
    listing = [_home]
    with plugin.get_storage('myshows.pcl') as storage:
        myshows = storage.get('myshows', [])
    with plugin.get_storage('tvshows.pcl') as tvshows:
        for index, show in enumerate(myshows):
            listing.append({'label': show[0],
                            'thumb': tvshows[show[2]]['poster'],
                            'fanart': tvshows[show[2]]['fanart'],
                            'art': {'banner': tvshows[show[2]]['banner'],
                                    'poster': tvshows[show[2]]['poster'],
                                    'landscape': tvshows[show[2]].get('landscape'),
                                    'clearart': tvshows[show[2]].get('clearart'),
                                    'clearlogo': tvshows[show[2]].get('clearlogo')},
                            'url': plugin.get_url(action='episodes',
                                                  mode='search',
                                                  search_imdb=show[2],
                                                  myshows='true'),
                            'info': {'video': {'tvshowtitle': tvshows[show[2]]['tvshowtitle'],
                                               'title': tvshows[show[2]]['tvshowtitle'],
                                               'plot': tvshows[show[2]]['plot'],
                                               'premiered': tvshows[show[2]]['premiered'],
                                               'year': int(tvshows[show[2]]['premiered'][:4])}},
                            'context_menu': [('Remove from "My Shows"...',
                            'RunScript({plugin_path}/libs/commands.py,myshows_remove,{config_dir},{index})'.format(
                            plugin_path=plugin.path,
                            config_dir=plugin.config_dir,
                            index=index
                            ))]
                            })
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
    return plugin.create_listing([_home], view_mode=_set_view_mode())


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
