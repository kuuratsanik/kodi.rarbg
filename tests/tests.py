# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# todo: re-factor tests
import sys
import os
import codecs
import json
import unittest
# Additional modules
import mock

_cwd = os.path.dirname(__file__)
_test_data = os.path.join(_cwd, 'test_data')
sys.path.append(os.path.join(os.path.dirname(_cwd), 'plugin.video.rarbg.tv'))


def fake_cached(duration=None):
    """
    Cached decorator stub
    """
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return inner_wrapper
    return outer_wrapper


with mock.patch('simpleplugin.Plugin') as mock_Plugin:
    mock_plugin = mock_Plugin.return_value
    mock_plugin.cached.side_effect = fake_cached
    mock_storage = mock.MagicMock()
    mock_storage.__enter__.return_value = {}
    mock_storage.__exit__.return_value = False
    mock_plugin.get_storage.return_value = mock_storage
    from libs import thetvdb


@mock.patch('libs.thetvdb.load_page')
class TheTVDBTestCase(unittest.TestCase):
    """Test thetvdb module"""
    def test_get_series_by_imdbid_with_data(self, mock_load_page):
        with codecs.open(os.path.join(_test_data, 'get_series_by_id.xml'), mode='rb', encoding='utf-8') as file_:
            xml = file_.read()
        mock_load_page.return_value = xml
        results = thetvdb.get_series_by_imdbid(None)
        self.assertIsNotNone(results)
        self.assertEqual(results['tvshowtitle'], 'Game of Thrones')

    def test_get_series_by_imdbid_without_data(self, mock_load_page):
        xml = '<?xml version="1.0" encoding="UTF-8" ?><Data></Data>'
        mock_load_page.return_value = xml
        self.assertIsNone(thetvdb.get_series_by_imdbid(None))

    def test_get_series_with_data(self, mock_load_page):
        with codecs.open(os.path.join(_test_data, 'get_series.xml'), mode='rb', encoding='utf-8') as file_:
            xml = file_.read()
        mock_load_page.return_value = xml
        results = thetvdb.get_series(None)
        self.assertNotEqual(results, [])
        self.assertEqual(len(results), 10)

    def test_get_series_without_data(self, mock_load_page):
        xml = '<?xml version="1.0" encoding="UTF-8" ?><Data></Data>'
        mock_load_page.return_value = xml
        self.assertEqual(thetvdb.get_series(None), [])


if __name__ == '__main__':
    unittest.main()
