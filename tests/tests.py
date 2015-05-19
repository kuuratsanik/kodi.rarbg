__author__ = 'romanmi'

import sys
import os
import base64
from datetime import timedelta
import unittest
# Additional modules
import mock

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugin.video.rarbg.tv'))

with mock.patch('sys.argv', ['plugin://plugin.video.rarbg.tv', '5', '']):
    import main
from libs import addon

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
        mock_episode_list_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5, '3')

    @mock.patch('main.views.episode_view')
    def test_calling_episode_page(self, mock_episode_view):
        url = 'https://www.rarbg.to/torrent/zx7bfge'
        main.router('?action=episode&url={0}'.format(base64.urlsafe_b64encode(url)))
        mock_episode_view.assert_called_with(5, url)

    @mock.patch('main.views.episode_list_view')
    def test_calling_episode_search_with_existing_query(self, mock_episode_list_view):
        main.router('?action=search_episodes&page=1&query=Test2')
        mock_episode_list_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5, '1', 'Test2')

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
        mock_episode_list_view.assert_called_with('plugin://plugin.video.rarbg.tv', 5, '1', 'Test1')
        # Test entering empty text from the on-screen Keyboard
        m_keyboard.getText.return_value = ''
        main.router('?action=search_episodes&page=1')
        m_notification.assert_called_with('Note!', 'Search cancelled', 'info', 3000)
        mock_endOfDirectory.assert_called_with(5, False)
        # Test cancelling on-screen Keyboard
        m_keyboard.getText.return_value = 'Test2'
        m_keyboard.isConfirmed.return_value = False
        main.router('?action=search_episodse&page=1')
        m_notification.assert_called_with('Note!', 'Search cancelled', 'info', 3000)
        mock_endOfDirectory.assert_called_with(5, False)


class AddonStorageTestCase(unittest.TestCase):
    """
    Test addon Storage class
    """
    def tearDown(self):
        os.remove(os.path.join(os.path.dirname(__file__), 'temp', 'storage.pcl'))
        os.remove(os.path.join(os.path.dirname(__file__), 'temp'))

    @mock.patch('libs.addon.Addon')
    def test_addon_storage(self, mock_Addon):
        mock_Addon.return_value.config_dir = os.path.join(os.path.dirname(__file__), 'temp')
        # Test storage initialization
        with addon.Storage() as storage1:
            storage1['item1'] = 'value1'
            self.assertEqual(storage1['item1'], 'value1')
        # Test existing storage
        with addon.Storage() as storage2:
            storage2['item2'] = 'value2'
            self.assertEqual(storage2['item2'], 'value2')


class AddonCahcedTestCase(unittest.TestCase):
    """
    Test cached decorator
    """
    @mock.patch('libs.addon.Storage')
    def test_cachde_decorator_(self, mock_Storage):
        storage = {}
        mock_Storage.return_value.__enter__.return_value = storage

        @addon.cached(1)
        def cached_function(arg):
            return 'test'

        # Test if function return value is stored in the cache
        cached_function('argument')
        self.assertTrue(storage['cache'])
        # Test if function return value is retrieved from the cache
        for key in storage['cache'].keys():
            value, timestamp = storage['cache'][key]
            storage['cache'][key] = ('altered', timestamp)
        self.assertEqual(cached_function('argument'), 'altered')
        # Test if function is called again if the cached value is expired
        for key in storage['cache'].keys():
            value, timestamp = storage['cache'][key]
            timestamp = timestamp - timedelta(minutes=10)
            storage['cache'][key] = ('altered', timestamp)
        self.assertEqual(cached_function('argument'), 'test')

if __name__ == '__main__':
    unittest.main()
