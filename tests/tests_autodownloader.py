# coding: utf-8
# Created on: 24.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
import json
from unittest import TestCase, expectedFailure
from mock import MagicMock, patch
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

__all__ = ['AutoDownloaderTestCase']

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'plugin.video.rarbg.tv'))
test_data = os.path.join(basedir, 'tests', 'test_data')

mock_get_torrents = MagicMock()
with open(os.path.join(test_data, 'torrents.json'), 'rb') as fo:
    mock_get_torrents.return_value = json.load(fo)
sys.modules['requests'] = MagicMock()
mock_addon = MagicMock()
mock_addon.config_dir = ''
mock_storage = MagicMock()
mock_addon.get_storage.return_value = mock_storage
mock_simpleplugin = MagicMock()
mock_simpleplugin.Addon.return_value = mock_addon
sys.modules['simpleplugin'] = mock_simpleplugin

from libs.autodownloader import filter_torrents


@patch('libs.autodownloader.get_torrents', mock_get_torrents)
@patch('libs.autodownloader.download_torrent')
@patch('libs.autodownloader.load_filters')
class AutoDownloaderTestCase(TestCase):
    def test_simple_filter(self, mock_load_filters, mock_download_torrent):
        filters = OrderedDict([('262407', {'save_path': '/foo/bar'})])
        mock_load_filters.return_value = filters
        mock_storage.__enter__.return_value = {}
        filter_torrents()
        mock_download_torrent.assert_called_with('magnet:?xt=urn:btih:022412cd217bbd14fc7e6d19f53c8b6b76bb22be&'
                                         'dn=Black.Sails.S03E05.XXIII.720p.STZ.WEBRip.AAC2.0.H264-DRHD%5Brartv%5D&'
                                                 'tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&'
                                                 'tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&'
                                                 'tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce',
                                                 '/foo/bar')
        mock_download_torrent.reset_mock()
        filters = OrderedDict((('foobar', {'save_path': '/foo/bar'}),))
        mock_load_filters.return_value = filters
        mock_storage.__enter__.return_value = {}
        filter_torrents()
        mock_download_torrent.assert_not_called()

    def test_additional_filter_criteria(self, mock_load_filters, mock_download_torrent):
        filters = OrderedDict([('269550', {'save_path': '/foo/bar', 'extra_filter': '720p'})])
        mock_load_filters.return_value = filters
        mock_storage.__enter__.return_value = {}
        filter_torrents()
        mock_download_torrent.assert_called_with('magnet:?xt=urn:btih:1d9bbb69e7c5518131268340e0125fcf2d9d615f&'
                                                 'dn=Bitten.S03E02.720p.HDTV.x264-KILLERS%5Brartv%5D&'
                                                 'tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&'
                                                 'tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&'
                                                 'tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce',
                                                 '/foo/bar')

    def test_exclude_criteria(self, mock_load_filters, mock_download_torrent):
        filters = OrderedDict([('269550', {'save_path': '/foo/bar', 'exclude': 'hdtv'})])
        mock_load_filters.return_value = filters
        mock_storage.__enter__.return_value = {}
        filter_torrents()
        mock_download_torrent.assert_not_called()

    @expectedFailure  # Todo: fix this
    def test_exclude_downloaded_episode(self, mock_load_filters, mock_download_torrent):
        filters = OrderedDict([('262407', {'save_path': '/foo/bar'})])
        mock_load_filters.return_value = filters
        mock_storage.__enter__.return_value = {'262407': [(3, 5)]}
        filter_torrents()
        mock_download_torrent.assert_not_called()
