# coding: utf-8
# Created on: 18.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
from unittest import TestCase
from mock import MagicMock, patch

__all__ = ['SetInfoTestCase', 'SetArtTestCase']

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'plugin.video.rarbg.tv'))

sys.modules['xbmc'] = MagicMock()
sys.modules['xbmcgui'] = MagicMock()
sys.modules['xbmcplugin'] = MagicMock()
sys.modules['simpleplugin'] = MagicMock()

with patch('simpleplugin.Plugin') as mock_Plugin:
    mock_plugin = MagicMock()
    mock_plugin.path = '/foo'
    mock_plugin.fanart = 'fanarg.jpg'
    mock_Plugin.return_value = mock_plugin
    from libs import actions


class SetInfoTestCase(TestCase):
    def setUp(self):
        self.torrent = {'episode_info': {'seasonnum': '3', 'epnum': '03'}, 'show_info': None, 'tvdb_episode_info': None}
        self.list_item = {'label': 'Castle.2009.S03E03.720p.mkv'}

    def test_setting_tvshow_info(self):
        self.torrent['show_info'] = {'SeriesName': 'Castle (2009)',
                                     'FirstAired': '2010-10-04'}
        actions._set_info(self.list_item, self.torrent)
        self.assertEqual(self.list_item['info']['video']['tvshowtitle'], 'Castle (2009)')
        self.assertEqual(self.list_item['info']['video']['year'], 2010)

    def test_setting_episode_info(self):
        self.torrent['tvdb_episode_info'] = {'Director': 'Bryan Spicer', 'Rating': '7.7'}
        actions._set_info(self.list_item, self.torrent)
        self.assertEqual(self.list_item['info']['video']['director'], 'Bryan Spicer')
        self.assertEqual(self.list_item['info']['video']['rating'], 7.7)

    def test_setting_episode_info_myshows(self):
        self.torrent['tvdb_episode_info'] = {'EpisodeName': 'Under the Gun'}
        actions._set_info(self.list_item, self.torrent, True)
        self.assertEqual(self.list_item['label'], 'Under the Gun')


class SetArtTestCase(TestCase):
    def setUp(self):
        self.torrent = {'episode_info': {'seasonnum': '3', 'epnum': '03'}, 'show_info': None, 'tvdb_episode_info': None}
        self.list_item = {}

    def test_setting_art_no_show_info(self):
        actions._set_art(self.list_item, self.torrent)
        self.assertIn('tv.png', self.list_item['thumb'])

    def test_seting_art_show_info_myshows(self):
        self.torrent['show_info'] = {'SeriesName': 'Castle (2009)', 'poster': 'poster.jpg'}
        self.torrent['tvdb_episode_info'] = None
        actions._set_art(self.list_item, self.torrent, True)
        self.assertEqual(self.list_item['thumb'], 'poster.jpg')
        self.assertEqual(self.list_item['art']['poster'], 'poster.jpg')
        self.torrent['tvdb_episode_info'] = {'EpisodeName': 'Under the Gun'}
        actions._set_art(self.list_item, self.torrent, True)
        self.assertEqual(self.list_item['thumb'], 'poster.jpg')
        self.torrent['tvdb_episode_info']['filename'] = 'screenshot.jpg'
        actions._set_art(self.list_item, self.torrent, True)
        self.assertEqual(self.list_item['thumb'], 'screenshot.jpg')
