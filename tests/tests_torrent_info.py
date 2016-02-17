# coding: utf-8
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
from unittest import TestCase
from mock import MagicMock, patch
from libs.exceptions import NoDataError

__all__ = ['ParseTorrentNameTestCase', 'AddShowInfoTestCase', 'AddEpisodeInfoTestCase']

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'plugin.video.rarbg.tv'))

sys.modules['xbmc'] = MagicMock()
sys.modules['simpleplugin'] = MagicMock()
sys.modules['libs.tvdb'] = MagicMock()

import libs.torrent_info as ti


def raise_no_data_error(*args, **kwargs):
    raise NoDataError


class ParseTorrentNameTestCase(TestCase):
    def test_parse_torrent_name(self):
        result = ti.parse_torrent_name('Foo.S05E06.mp4')
        self.assertEqual(result.name, 'Foo')
        self.assertEqual(result.season, '05')
        self.assertEqual(result.episode, '06')
        result = ti.parse_torrent_name('Bar.03x07.mkv')
        self.assertEqual(result.name, 'Bar')
        self.assertEqual(result.season, '03')
        self.assertEqual(result.episode, '07')

    def test_parse_torrent_name_invalid_episode_name(self):
        self.assertRaises(ValueError, ti.parse_torrent_name, 'Foo.Bar')


class AddShowInfoTestCase(TestCase):
    def test_adding_existing_show_info(self):
        torrent = {'episode_info': {'tvdb': '82607'}}
        tvshows = {'82607': {'SeriesName': 'Castle (2009)'}}
        ti.add_show_info(torrent, tvshows)
        self.assertEqual(torrent['show_info']['SeriesName'], 'Castle (2009)')

    @patch('libs.torrent_info.tvdb.get_series')
    def test_getting_missing_show_info(self, mock_get_series):
        torrent = {'episode_info': {'tvdb': '121361', 'imdb': 'tt0944947'}}
        tvshows = {}
        mock_get_series.return_value = {'SeriesName': 'Game of Thrones'}
        ti.add_show_info(torrent, tvshows)
        self.assertEqual(torrent['show_info']['SeriesName'], 'Game of Thrones')
        self.assertEqual(tvshows['121361']['SeriesName'], 'Game of Thrones')
        self.assertEqual(tvshows['121361']['IMDB_ID'], 'tt0944947')

    @patch('libs.torrent_info.tvdb.get_series')
    def test_get_series_returned_no_data(self, mock_get_series):
        torrent = {'episode_info': {'tvdb': '121361'}}
        tvshows = {}
        mock_get_series.side_effect = raise_no_data_error
        ti.add_show_info(torrent, tvshows)
        self.assertIs(torrent['show_info'], None)


class AddEpisodeInfoTestCase(TestCase):
    pass
