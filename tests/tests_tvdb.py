# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import os
import codecs
from unittest import TestCase
from mock import MagicMock, patch

__all__ = ['GetSeriesTestCase', 'GetEpisodeTestCase', 'SearchSeriesTestCase']

cwd = os.path.dirname(os.path.abspath(__file__))
test_data = os.path.join(cwd, 'test_data')
sys.path.append(os.path.join(os.path.dirname(cwd), 'plugin.video.rarbg.tv'))

from libs.rarbg_exceptions import NoDataError, Http404Error

sys.modules['libs.utilities'] = MagicMock()

from libs.tvdb import get_series, get_episode, search_series


def raise404(*args, **kwargs):
    raise Http404Error


@patch('libs.tvdb.load_page')
class GetSeriesTestCase(TestCase):
    def test_get_series(self, mock_load_page):
        with codecs.open(os.path.join(test_data, 'get_series.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        result = get_series('82607')
        self.assertEqual(result['SeriesName'], 'Castle (2009)')
        self.assertEqual(result['poster'], 'http://thetvdb.com/banners/posters/83462-16.jpg')

    def test_get_series_invalid(self, mock_load_page):
        with codecs.open(os.path.join(test_data, 'invalid.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        self.assertRaises(NoDataError, get_series, '82607')

    def test_get_series_tvdb_returns_404(self, mock_load_page):
        mock_load_page.side_effect = raise404
        self.assertRaises(NoDataError, get_series, '82607')


@patch('libs.tvdb.load_page')
class GetEpisodeTestCase(TestCase):
    def test_get_episode(self, mock_load_page):
        with codecs.open(os.path.join(test_data, 'get_episode.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        result = get_episode('83462', '3', '3')
        self.assertEqual(result['EpisodeName'], 'Under the Gun')
        self.assertEqual(result['filename'], 'http://thetvdb.com/banners/episodes/83462/2744851.jpg')

    def test_get_episode_invalid(self, mock_load_page):
        with codecs.open(os.path.join(test_data, 'invalid.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        self.assertRaises(NoDataError, get_episode, '82607', '3', '3')

    def test_get_episode_tvdb_returns_404(self, mock_load_page):
        mock_load_page.side_effect = raise404
        self.assertRaises(NoDataError, get_episode, '82607', '3', '3')


@patch('libs.tvdb.load_page')
class SearchSeriesTestCase(TestCase):
    def test_search_series(self, mock_load_page):
        with codecs.open(os.path.join(test_data, 'search_series.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        result = search_series('Castle')
        self.assertEqual(len(result), 10)

    def test_search_series_invalid(self, mock_load_page):
        with codecs.open(os.path.join(test_data, 'invalid.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        self.assertRaises(NoDataError, search_series, 'FooBar')
