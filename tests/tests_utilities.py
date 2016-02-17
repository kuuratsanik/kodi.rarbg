# coding: utf-8
# Module: tests_utilities
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
from unittest import TestCase
from mock import MagicMock, patch
from libs.exceptions import Http404Error

__all__ = ['LoadPageTestCase']

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'plugin.video.rarbg.tv'))

sys.modules['requests'] = MagicMock()
sys.modules['xbmc'] = MagicMock()
sys.modules['simpleplugin'] = MagicMock()

from libs.utilities import load_page

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0',
    'Accept-Charset': 'UTF-8',
    'Accept': 'text/html,application/json,application/xml',
    'Accept-Language': 'en-US, en',
    'Accept-Encoding': 'gzip, deflate'
}


@patch('libs.utilities.requests.get')
class LoadPageTestCase(TestCase):
    def setUp(self):
        self.mock_response = MagicMock()

    def test_load_page_json(self, mock_get):
        self.mock_response.headers = {'content-type': 'application/json'}
        self.mock_response.json.return_value = {'foo': 'bar'}
        mock_get.return_value = self.mock_response
        result = load_page('foo')
        mock_get.assert_called_with('foo', params=None, headers=HEADERS, verify=False)
        self.assertEqual(result['foo'], 'bar')

    def test_load_page_xml(self, mock_get):
        self.mock_response.headers = {'content-type': 'application/xml'}
        self.mock_response.text = '<foo>Bar</foo>'
        mock_get.return_value = self.mock_response
        result = load_page('bar')
        self.assertEqual(result, '<foo>Bar</foo>')

    def test_page_not_found(self, mock_get):
        self.mock_response.status_code = 404
        mock_get.return_value = self.mock_response
        self.assertRaises(Http404Error, load_page, 'foo')

    def test_pass_headers(self, mock_get):
        headers = {'content-type': 'application/json'}
        HEADERS.update(headers)
        load_page('foo', headers=headers)
        mock_get.assert_called_with('foo', params=None, headers=HEADERS, verify=False)
