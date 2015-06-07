# -*- coding: utf-8 -*-
# Module: views
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
from base64 import urlsafe_b64encode
#
import xbmcplugin
import xbmcgui
from xbmc import LOGERROR
#
import parser
from addon import Addon, Storage

__addon__ = Addon()
_icons = __addon__.icons_dir


def root_view(plugin_url, plugin_handle):
    """
    Plugin root view
    :return:
    """
    episodes_item = xbmcgui.ListItem(label='[Recent episodes]', thumbnailImage=os.path.join(_icons, 'tv.png'))
    episodes_item.setArt({'fanart': __addon__.fanart})
    episodes_url = '{0}?action=episode_list&page=1'.format(plugin_url)
    xbmcplugin.addDirectoryItem(plugin_handle, episodes_url, episodes_item, isFolder=True)
    search_item = xbmcgui.ListItem(label='[Search episodes]', thumbnailImage=os.path.join(_icons, 'search.png'))
    search_item.setArt({'fanart': __addon__.fanart})
    search_url = '{0}?action=search_episodes&page=1'.format(plugin_url)
    xbmcplugin.addDirectoryItem(plugin_handle, search_url, search_item, isFolder=True)
    myshows_item = xbmcgui.ListItem(label='[My Shows]', thumbnailImage=os.path.join(_icons, 'bookmarks.png'))
    myshows_item.setArt({'fanart': __addon__.fanart})
    myshows_url = '{0}?action=my_shows'.format(plugin_url)
    xbmcplugin.addDirectoryItem(plugin_handle, myshows_url, myshows_item, isFolder=True)
    xbmcplugin.endOfDirectory(plugin_handle)


def episode_list_view(plugin_url, plugin_handle, page, search_query='', imdb=''):
    """
    The list of episode receases by most recent first
    :param plugin_url:
    :param plugin_handle:
    :return:
    """
    # Add 'Home' item
    home_item = xbmcgui.ListItem(label='<< Home',
                                 thumbnailImage=os.path.join(_icons, 'home.png'),
                                 iconImage=os.path.join(_icons, 'home.png'))
    xbmcplugin.addDirectoryItem(plugin_handle, plugin_url, home_item, isFolder=True)
    episodes = parser.load_episodes(page, search_query, imdb)  # Get episodes
    if episodes['episodes']:
        if episodes['prev']:  # Previous page if any
            prev_item = xbmcgui.ListItem(label='{0} < Prev'.format(episodes['prev']),
                                         thumbnailImage=os.path.join(_icons, 'previous.png'),
                                         iconImage=os.path.join(_icons, 'previous.png'))
            prev_item.setArt({'fanart': __addon__.fanart})
            if search_query:
                prev_url = '{0}?action=search_episodes&query={1}&page={2}'.format(plugin_url, search_query,
                                                                                 episodes['prev'])
            elif imdb:
                prev_url = '{0}?action=episode_list&imdb={1}&page={2}'.format(plugin_url, imdb, episodes['prev'])
            else:
                prev_url = '{0}?action=episode_list&page={1}'.format(plugin_url, episodes['prev'])
            xbmcplugin.addDirectoryItem(plugin_handle, prev_url, prev_item, isFolder=True)
        # Populate the episode list
        for episode in episodes['episodes']:
            if int(episode['seeders']) <= 10:
                episode['seeders'] = '[COLOR=red]{0}[/COLOR]'.format(episode['seeders'])
            elif int(episode['seeders']) <= 25:
                episode['seeders'] = '[COLOR=yellow]{0}[/COLOR]'.format(episode['seeders'])
            thumb = episode['thumb'] if episode['thumb'] else os.path.join(__addon__.icons_dir, 'tv.png')
            list_item = xbmcgui.ListItem(label='{0} [COLOR=gray]({1}|S:{2}/L:{3})[/COLOR]'.format(episode['title'],
                                                                                                  episode['size'],
                                                                                                  episode['seeders'],
                                                                                                  episode['leechers']),
                                         thumbnailImage=thumb,
                                         iconImage=thumb)
            list_item.setInfo('video', episode['info'])
            list_item.setArt({'fanart': __addon__.fanart})
            url = '{0}?action=episode&url={1}'.format(plugin_url, urlsafe_b64encode(episode['link']))
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, isFolder=True)
        if episodes['next']:  # Next page if any
            next_item = xbmcgui.ListItem(label='Next > {0}'.format(episodes['next']),
                                         thumbnailImage=os.path.join(_icons, 'next.png'),
                                         iconImage=os.path.join(_icons, 'next.png'))
            next_item.setArt({'fanart': __addon__.fanart})
            if search_query:
                next_url = '{0}?action=search_episodes&query={1}&page={2}'.format(plugin_url, search_query,
                                                                                 episodes['next'])
            elif imdb:
                next_url = '{0}?action=episode_list&imdb={1}&page={2}'.format(plugin_url, imdb, episodes['next'])
            else:
                next_url = '{0}?action=episode_list&page={1}'.format(plugin_url, episodes['next'])
            xbmcplugin.addDirectoryItem(plugin_handle, next_url, next_item, isFolder=True)
    else:
        xbmcgui.Dialog().notification('Error!', 'No episodes to dislpay!', 'error', 3000)
        __addon__.log('Empty episode list returned.', LOGERROR)
    xbmcplugin.endOfDirectory(plugin_handle)


def episode_view(plugin_handle, url):
    """
    Episode page

    :param plugin_handle:
    :param url:
    :return:
    """
    episode_data = parser.load_episode_page(url)
    if episode_data['filename']:
        try:
            if int(episode_data['seeders']) <= 10:
                episode_data['seeders'] = '[COLOR=red]{0}[/COLOR]'.format(episode_data['seeders'])
            elif int(episode_data['seeders']) <= 25:
                episode_data['seeders'] = '[COLOR=yellow]{0}[/COLOR]'.format(episode_data['seeders'])
        except ValueError:
            pass
        poster = episode_data['poster'] if episode_data['poster'] else os.path.join(__addon__.icons_dir, 'tv.png')
        ep_item = xbmcgui.ListItem(label='{0} [COLOR=gray]({1}|S:{2}/L:{3})[/COLOR]'.format(episode_data['filename'],
                                                                                            episode_data['size'],
                                                                                            episode_data['seeders'],
                                                                                            episode_data['leechers']),
                                   thumbnailImage=poster,
                                   iconImage=poster)
        ep_item.setInfo('video', episode_data['info'])
        ep_item.setArt({'fanart': __addon__.fanart})
        ep_item.addContextMenuItems([
            ('Add to "My Shows"',
             'RunScript({0}/libs/commands.py,myshows_add,{1},{2},{3},{4})'.format(
                 __addon__.addon_dir,
                 __addon__.config_dir,
                 episode_data['info']['title'],
                 episode_data['imdb'],
                 episode_data['poster']))])
        url = 'plugin://plugin.video.yatp/?action=play&torrent={torrent}&title={title}&thumb={poster}'.format(
            torrent=urlsafe_b64encode(episode_data['torrent']),
            title=urlsafe_b64encode(episode_data['info']['title']),
            poster=urlsafe_b64encode(episode_data['poster']))
        try:
            url += '&season={0}'.format(episode_data['info']['season'])
        except KeyError:
            pass
        try:
            url += '&episode={0}'.format(episode_data['info']['episode'])
        except KeyError:
            pass
        xbmcplugin.addDirectoryItem(plugin_handle, url, ep_item, isFolder=False)
    else:
        xbmcgui.Dialog().notification('Error!', 'No episode data to dislpay!', 'error', 3000)
        __addon__.log('Empty episode data returned.', LOGERROR)
    xbmcplugin.endOfDirectory(plugin_handle)


def my_shows_view(plugin_url, plugin_handle):
    """
    The list of favorite TV shows
    :return:
    """
    home_item = xbmcgui.ListItem(label='<< Home',
                                 thumbnailImage=os.path.join(_icons, 'home.png'),
                                 iconImage=os.path.join(_icons, 'home.png'))
    xbmcplugin.addDirectoryItem(plugin_handle, plugin_url, home_item, isFolder=True)
    with Storage(__addon__.config_dir) as storage:
        try:
            myshows = storage['myshows']
        except KeyError:
            pass
        else:
            for index, show in enumerate(myshows):
                list_item = xbmcgui.ListItem(label=show[0],
                                             thumbnailImage=show[2],
                                             iconImage=show[2])
                list_item.setArt({'fanart': __addon__.fanart})
                url = '{0}?action=episode_list&page=1&imdb={1}'.format(plugin_url, show[1])
                list_item.addContextMenuItems([('Remove from "My Shows"',
                                                'RunScript({0}/libs/commands.py,myshows_remove,{1},{2})'.format(
                                                    __addon__.addon_dir,
                                                    __addon__.config_dir,
                                                    index))])
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, isFolder=True)
    xbmcplugin.endOfDirectory(plugin_handle)
