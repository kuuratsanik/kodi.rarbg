# coding: utf-8
# Created on: 18.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
import json
from unittest import TestCase
from mock import MagicMock, patch

__all__ = ['SetInfoTestCase', 'SetArtTestCase', 'SetStreamInfoTestCase', 'RootTestCase', 'EpisodesTestCase',
           'MyShowsTestCase']

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'plugin.video.rarbg.tv'))
test_data = os.path.join(basedir, 'tests', 'test_data')

sys.modules['xbmc'] = MagicMock()
sys.modules['xbmcgui'] = MagicMock()
sys.modules['xbmcplugin'] = MagicMock()
sys.modules['simpleplugin'] = MagicMock()
sys.modules['libs.gui'] = MagicMock()


def create_listing(listing, succeeded=True, update_listing=False, cache_to_disk=False, sort_methods=None,
                   view_mode=None, content=None):
    return {'listing': listing, 'succeeded': succeeded, 'update_listing': update_listing,
            'cache_to_disk': cache_to_disk, 'sort_methods': sort_methods, 'view_mode': view_mode,
            'content': content}


with patch('simpleplugin.Plugin') as mock_Plugin, patch('simpleplugin.Addon') as mock_Addon:
    mock_plugin = MagicMock()
    mock_plugin.path = '/foo'
    mock_plugin.config_dir = '/bar'
    mock_plugin.fanart = 'fanarg.jpg'
    mock_storage = MagicMock()
    mock_plugin.get_storage.return_value = mock_storage
    mock_plugin.create_listing.side_effect = create_listing
    mock_Plugin.return_value = mock_plugin
    mock_Addon.return_value = mock_plugin
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
        self.assertTrue('tv.png' in self.list_item['thumb'])

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


class SetStreamInfoTestCase(TestCase):
    def test_720p(self):
        torrent = {'title': 'Castle.2009.S03E04.720p.mkv'}
        list_item = {}
        actions._set_stream_info(list_item, torrent)
        self.assertEqual(list_item['stream_info']['video']['height'], 720)

    def test_1080p(self):
        torrent = {'title': 'Castle.2009.S03E04.1080p.mkv'}
        list_item = {}
        actions._set_stream_info(list_item, torrent)
        self.assertEqual(list_item['stream_info']['video']['height'], 1080)

    def test_sd(self):
        torrent = {'title': 'Castle.2009.S03E04.HDTV.mp4'}
        list_item = {}
        actions._set_stream_info(list_item, torrent)
        self.assertEqual(list_item['stream_info']['video']['height'], 480)

    def test_h264(self):
        torrent = {'title': 'Castle.2009.S03E04.x264.mp4'}
        list_item = {}
        actions._set_stream_info(list_item, torrent)
        self.assertEqual(list_item['stream_info']['video']['codec'], 'h264')

    def test_mpeg2(self):
        torrent = {'title': 'Castle.2009.S03E04.MPEG2.mp4'}
        list_item = {}
        actions._set_stream_info(list_item, torrent)
        self.assertEqual(list_item['stream_info']['video']['codec'], 'mpeg2video')

    def test_divx(self):
        torrent = {'title': 'Castle.2009.S03E04.DIVX.mp4'}
        list_item = {}
        actions._set_stream_info(list_item, torrent)
        self.assertEqual(list_item['stream_info']['video']['codec'], 'divx')


class RootTestCase(TestCase):
    def test_root_action(self):
        context = actions.root({})
        self.assertEqual(len(context['listing']), 4)


class EpisodesTestCase(TestCase):
    @patch('libs.actions.get_torrents')
    def test_episodes_action(self, mock_get_torrents):
        with open(os.path.join(test_data, 'torrents.json'), mode='rb') as fileobj:
            torrents = json.load(fileobj)
        mock_get_torrents.return_value = torrents
        context = actions.episodes({'mode': 'list'})
        self.assertEqual(len(list(context['listing'])), 71)
        context = actions.episodes({'mode': 'list', 'myshows': True})
        self.assertEqual(len(list(context['listing'])), 71)


class MyShowsTestCase(TestCase):
    def test_my_shows_action(self):
        mock_storage.__enter__.return_value = {'myshows': ['83462'],
                                               '83462': {
                                                   'SeriesID': '75394',
                                                   'Network': 'ABC (US)',
                                                   'IMDB_ID': 'tt1219024',
                                                   'Actors': '|Nathan Fillion|Stana Katic|Molly C. Quinn|Penny Johnson|'
                                                             'Jon Huertas|Seamus Dever|Tamala Jones|Susan Sullivan|'
                                                             'Ruben Santiago-Hudson|',
                                                   'id': '83462',
                                                   'Status': 'Continuing',
                                                   'Airs_Time': '10:00 PM',
                                                   'fanart': 'http://thetvdb.com/banners/fanart/original/83462-41.jpg',
                                                   'lastupdated': '1455610116',
                                                   'FirstAired': '2009-03-09',
                                                   'RatingCount': '446',
                                                   'Genre': '|Comedy|Crime|Drama|',
                                                   'added': '2008-10-17 15:05:50',
                                                   'Language': 'en',
                                                   'Airs_DayOfWeek': 'Monday',
                                                   'tms_wanted_old': '1',
                                                   'poster': 'http://thetvdb.com/banners/posters/83462-16.jpg',
                                                   'ContentRating': 'TV-PG',
                                                   'addedBy': '3071',
                                                   'SeriesName': 'Castle (2009)',
                                                   'Runtime': '45',
                                                   'banner': 'http://thetvdb.com/banners/graphical/83462-g20.jpg',
                                                   'NetworkID': '',
                                                   'Rating': '8.8',
                                                   'zap2it_id': 'EP01085588',
                                                   'Overview': "Rick Castle is one of the world's most successful crime"
                                                               " authors. But when his rock star lifestyle isn't enough,"
                                                               " this bad boy goes looking for new trouble and finds it"
                                                               " working with smart, beautiful Detective Kate Beckett."
                                                               " Inspired by her professional record and intrigued by"
                                                               " her buttoned-up personality, Castle's found the model"
                                                               " for his bold new character whether she likes it or not."
                                                               " Now with the mayor's permission, Castle is helping "
                                                               "solve crime with his own twist."}}
        mock_storage.__exit__.return_value = False
        context = actions.my_shows({'action': 'my_shows'})
        self.assertEqual(len(context['listing']), 2)
