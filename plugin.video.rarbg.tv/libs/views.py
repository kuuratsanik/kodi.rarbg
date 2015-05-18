# -*- coding: utf-8 -*-
# Module: views
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from base64 import urlsafe_b64encode
import xbmcplugin
import xbmcgui
import parser


def root_view(plugin_url, plugin_handle):
    """
    Plugin root view
    :return:
    """
    episodes_item = xbmcgui.ListItem(label='[TV Episodes]')
    url = '{0}?action=episode_list&page=1'.format(plugin_url)
    xbmcplugin.addDirectoryItem(plugin_handle, url, episodes_item, isFolder=True)
    xbmcplugin.endOfDirectory(plugin_handle, True)


def episode_list_view(plugin_url, plugin_handle, page):
    """
    The list of episode receases by most recent first
    :param plugin_url:
    :param plugin_handle:
    :return:
    """
    home_item = xbmcgui.ListItem(label='<< Home')
    xbmcplugin.addDirectoryItem(plugin_handle, plugin_url, home_item, isFolder=True)
    episodes = parser.load_episodes(page)
    if episodes['episodes']:
        if episodes['prev']:
            prev_item = xbmcgui.ListItem(label='{0} < Prev'.format(episodes['prev']))
            prev_url = '{0}?action=episode_list&page={1}'.format(plugin_url, episodes['prev'])
            xbmcplugin.addDirectoryItem(plugin_handle, prev_url, prev_item, isFolder=True)
        for episode in episodes['episodes']:
            list_item = xbmcgui.ListItem(label=episode['title'],
                                         iconImage=episode['thumb'],
                                         thumbnailImage=episode['thumb'])
            list_item.setInfo('video', episode['info'])
            url = '{0}?action=episode&url={1}'.format(plugin_url, urlsafe_b64encode(episode['link']))
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, isFolder=True)
        if episodes['next']:
            prev_item = xbmcgui.ListItem(label='Next > {0}'.format(episodes['next']))
            next_url = '{0}?action=episode_list&page={1}'.format(plugin_url, episodes['next'])
            xbmcplugin.addDirectoryItem(plugin_handle, next_url, prev_item, isFolder=True)
    else:
        xbmcgui.Dialog().notification('Error!', 'No episodes to dislpay!', 'error', 3000)
    xbmcplugin.endOfDirectory(plugin_handle, True)


def episode_view(plugin_handle, url):
    """
    Episode page
    :param plugin_url:
    :param plugin_handle:
    :param url:
    :return:
    """
    episode_data = parser.load_episode_page(url)
    ep_item = xbmcgui.ListItem(label=episode_data['filename'],
                               thumbnailImage=episode_data['poster'],
                               iconImage=episode_data['poster'])
    ep_item.setInfo('video', episode_data['info'])
    url = 'plugin://plugin.video.yatp/?action=play&torrent={0}'.format(urlsafe_b64encode(episode_data['torrent']))
    xbmcplugin.addDirectoryItem(plugin_handle, url, ep_item, isFolder=False)
    xbmcplugin.endOfDirectory(plugin_handle, True)
