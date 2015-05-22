__author__ = 'romanmi'

import sys
import os
import base64
import json
import unittest
# Additional modules
import mock

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugin.video.rarbg.tv'))
with mock.patch('sys.argv', ['plugin://plugin.video.rarbg.tv', '5', '']):
    with mock.patch('xbmcaddon.Addon') as mock_Addon:
        with mock.patch('libs.addon.Addon') as mock_myAddon:
            mock_Addon.return_value.getAddonInfo.return_value = 'test'
            mock_storage = mock.MagicMock()
            mock_storage.__enter__.return_value = {}
            mock_myAddon.return_value.get_storage.return_value = mock_storage
            mock_myAddon.return_value.config_dir = 'test'
            import main
            import libs.webclient


class MainRouterTestCase(unittest.TestCase):
    """
    Test main.router() function
    """
    @mock.patch('main.views.root_view')
    def test_calling_plugin_root(self, mock_root_view):
        main.router('')
        mock_root_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5)

    @mock.patch('main.views.episode_list_view')
    def test_calling_episode_list(self, mock_episode_list_view):
        main.router('?action=episode_list&page=3')
        mock_episode_list_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5, '3', imdb='')

    @mock.patch('main.views.episode_view')
    def test_calling_episode_page(self, mock_episode_view):
        url = 'https://www.rarbg.to/torrent/zx7bfge'
        main.router('?action=episode&url={0}'.format(base64.urlsafe_b64encode(url)))
        mock_episode_view.assert_called_with(5, url)

    @mock.patch('main.views.episode_list_view')
    def test_calling_episode_search_with_existing_query(self, mock_episode_list_view):
        main.router('?action=search_episodes&page=1&query=Test2')
        mock_episode_list_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5, '1', search_query='Test2')

    @mock.patch('main.xbmcplugin.endOfDirectory')
    @mock.patch('main.xbmcgui.Dialog')
    @mock.patch('main.xbmc.Keyboard')
    @mock.patch('main.views.episode_list_view')
    def test_calling_episode_search_with_empty_query(self, mock_episode_list_view, mock_Keyboard, mock_Dialog,
                                                     mock_endOfDirectory):
        m_keyboard = mock_Keyboard.return_value
        m_notification = mock_Dialog.return_value.notification
        # Test calling entering entering a query from the on-screen Keyboard
        m_keyboard.getText.return_value = 'Test1'
        m_keyboard.isConfirmed.return_value = True
        main.router('?action=search_episodes&page=1')
        mock_episode_list_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5, '1', search_query='Test1')
        # Test entering empty text from the on-screen Keyboard
        m_keyboard.getText.return_value = ''
        main.router('?action=search_episodes&page=1')
        m_notification.assert_called_with('Note!', 'Search cancelled', 'info', 3000)
        mock_endOfDirectory.assert_called_with(5, False)
        # Test cancelling on-screen Keyboard
        m_keyboard.getText.return_value = 'Test2'
        m_keyboard.isConfirmed.return_value = False
        main.router('?action=search_episodes&page=1')
        m_notification.assert_called_with('Note!', 'Search cancelled', 'info', 3000)
        mock_endOfDirectory.assert_called_with(5, False)


class WebClientTestCase(unittest.TestCase):
    """
    Test web-client
    """
    def test_load_page_get_request(self):
        page = libs.webclient.load_page('http://httpbin.org/html')
        self.assertTrue('Herman Melville' in page)

    def test_load_page_post_request(self):
        post_data = {'param': 'value'}
        page = libs.webclient.load_page('http://httpbin.org/post', method='post', data=post_data)
        self.assertEqual(json.loads(page)['form']['param'], 'value')


if __name__ == '__main__':
    unittest.main()
