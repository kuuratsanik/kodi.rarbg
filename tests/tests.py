__author__ = 'romanmi'
# todo: re-factor tests
import sys
import os
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
    mock_plugin.get_storage.return_value = mock_storage
    from libs import webclient
    from libs import rarbg


class WebClientTestCase(unittest.TestCase):
    """
    Test web-client
    """
    def test_load_page_get_request(self):
        page = webclient.load_page('http://httpbin.org/html')
        self.assertTrue('Herman Melville' in page)

    def test_load_page_post_request(self):
        post_data = {'param': 'value'}
        contents = webclient.load_page('http://httpbin.org/post', method='post', data=post_data)
        self.assertEqual(contents['form']['param'], 'value')


class RarbgApiTestCase(unittest.TestCase):
    """
    Test Rarbg API access
    """
    def test_getting_rarbg_apikey(self):
        token = rarbg.get_token()
        self.assertTrue(isinstance(token, unicode))


if __name__ == '__main__':
    unittest.main()
