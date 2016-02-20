# coding: utf-8
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
from unittest import TestCase
from mock import MagicMock, patch

__all__ = ['ParseTorrentNameTestCase', 'AddShowInfoTestCase', 'AddEpisodeInfoTestCase', 'DeduplicateTorrentsTestCase']

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'plugin.video.rarbg.tv'))

sys.modules['xbmc'] = MagicMock()
sys.modules['simpleplugin'] = MagicMock()
sys.modules['libs.tvdb'] = MagicMock()

with patch('simpleplugin.Plugin') as mock_Plugin:
    mock_plugin = MagicMock()
    mock_plugin.path = os.path.join(basedir, 'plugin.video.rarbg.tv')
    mock_Plugin.return_value = mock_plugin
    import libs.torrent_info as ti
    from libs.exceptions import NoDataError


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
        torrent = {u'episode_info': {u'tvdb': u'82607'}}
        tvshows = {u'82607': {u'SeriesName': u'Castle (2009)'}}
        ti.add_show_info(torrent, tvshows)
        self.assertEqual(torrent['show_info']['SeriesName'], 'Castle (2009)')

    @patch('libs.torrent_info.tvdb.get_series')
    def test_getting_missing_show_info(self, mock_get_series):
        torrent = {u'episode_info': {u'tvdb': u'121361', u'imdb': u'tt0944947'}}
        tvshows = {}
        mock_get_series.return_value = {'SeriesName': 'Game of Thrones'}
        ti.add_show_info(torrent, tvshows)
        self.assertEqual(torrent['show_info']['SeriesName'], 'Game of Thrones')
        self.assertEqual(tvshows['121361']['SeriesName'], 'Game of Thrones')
        self.assertEqual(tvshows['121361']['IMDB_ID'], 'tt0944947')

    @patch('libs.torrent_info.tvdb.get_series')
    def test_get_series_returnes_no_data(self, mock_get_series):
        torrent = {u'title': u'castle.s03e03', u'episode_info': {u'tvdb': u'121361'}}
        tvshows = {}
        mock_get_series.side_effect = raise_no_data_error
        ti.add_show_info(torrent, tvshows)
        self.assertIs(torrent['show_info'], None)


class AddEpisodeInfoTestCase(TestCase):
    def test_adding_existing_episode_info(self):
        torrent = {u'episode_info': {u'tvdb': u'82607', u'seasonnum': u'3', u'epnum': u'03'}}
        episodes = {'82607-3x03': {'EpisodeName': 'Under the Gun'}}
        ti.add_episode_info(torrent, episodes)
        self.assertEqual(torrent['tvdb_episode_info']['EpisodeName'], 'Under the Gun')

    @patch('libs.torrent_info.tvdb.get_episode')
    def test_getting_missing_episode_info(self, mock_get_episode):
        torrent = {u'episode_info': {u'tvdb': u'82607', u'seasonnum': u'3', u'epnum': u'03'}}
        episodes = {}
        mock_get_episode.return_value = {'EpisodeName': 'Under the Gun'}
        ti.add_episode_info(torrent, episodes)
        self.assertEqual(torrent['tvdb_episode_info']['EpisodeName'], 'Under the Gun')
        self.assertEqual(episodes['82607-3x03']['EpisodeName'], 'Under the Gun')

    @patch('libs.torrent_info.tvdb.get_episode')
    def test_get_episode_rerurnes_no_data(self, mock_get_episode):
        torrent = {u'title': u'castle.s03e03', u'episode_info': {u'tvdb': u'82607',
                                                                 u'seasonnum': u'3',
                                                                 u'epnum': u'03'}}
        episodes = {}
        mock_get_episode.side_effect = raise_no_data_error
        ti.add_episode_info(torrent, episodes)
        self.assertIs(torrent['tvdb_episode_info'], None)


class DeduplicateTorrentsTestCase(TestCase):
    def test_torrents_missing_episode_or_tvdb_imdb_id(self):
        torrents = [{}]
        result = ti.deduplicate_torrents(torrents)
        self.assertSequenceEqual(result, [])
        torrents[0]['episode_info'] = {}
        result = ti.deduplicate_torrents(torrents)
        self.assertSequenceEqual(result, [])
        torrents[0]['episode_info'] = {'tvdb': '12345'}
        self.assertSequenceEqual(result, [])

    def test_torrents_are_not_episodes(self):
        torrents = [{'title': 'FooBar', 'episode_info': {'tvdb': '12345', 'imdb': 'tt12345'}}]
        result = ti.deduplicate_torrents(torrents)
        self.assertSequenceEqual(result, [])

    def test_torrents_are_episodes(self):
        torrents1 = [{'title': 'FooBar', 'episode_info': {'tvdb': '12345',
                                                         'imdb': 'tt12345',
                                                         'seasonnum': '01',
                                                         'epnum': '01'}}]
        result = ti.deduplicate_torrents(torrents1)
        self.assertSequenceEqual(result, torrents1)
        torrents2 = [{'title': 'Foo.s01e01.mp4', 'episode_info': {'tvdb': '12345', 'imdb': 'tt12345'}}]
        result = ti.deduplicate_torrents(torrents2)
        self.assertEqual(result[0]['episode_info']['seasonnum'], '01')
        self.assertEqual(result[0]['episode_info']['epnum'], '01')

    def test_deduplication_based_on_seeders(self):
        torrents = [
            {'title': 'Foo.s01e01.avi', 'episode_info': {'tvdb': '12345', 'imdb': 'tt12345'}, 'seeders': 10},
            {'title': 'Foo.s01e01.mp4', 'episode_info': {'tvdb': '12345', 'imdb': 'tt12345'}, 'seeders': 20},
        ]
        result = ti.deduplicate_torrents(torrents)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['seeders'], 20)

    def test_differentiating_sd_and_hd_torrents(self):
        torrents = [
            {'title': 'Foo.s01e01.mp4', 'episode_info': {'tvdb': '12345', 'imdb': 'tt12345'}, 'seeders': 10},
            {'title': 'Foo.s01e01.720p.mkv', 'episode_info': {'tvdb': '12345', 'imdb': 'tt12345'}, 'seeders': 20},
        ]
        result = ti.deduplicate_torrents(torrents)
        self.assertEqual(len(result), 2)
