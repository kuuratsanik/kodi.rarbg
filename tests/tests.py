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

with mock.patch('simpleplugin.Plugin') as mock_Plugin:
    with mock.patch('libs.webclient.Dialog') as mock_Dialog:
        mock_plugin = mock_Plugin.return_value
        mock_storage = mock.MagicMock()
        mock_storage.__enter__.return_value = {}
        mock_plugin.get_storage.return_value = mock_storage
        from libs import webclient
        from libs import parser

class WebClientTestCase(unittest.TestCase):
    """
    Test web-client
    """
    def test_load_page_get_request(self):
        page = webclient.load_page('http://httpbin.org/html')
        self.assertTrue('Herman Melville' in page)

    def test_load_page_post_request(self):
        post_data = {'param': 'value'}
        page = webclient.load_page('http://httpbin.org/post', method='post', data=post_data)
        self.assertEqual(json.loads(page)['form']['param'], 'value')


class ParserTestCase(unittest.TestCase):
    """
    Test parser function
    """
    def test_parse_episodes_list(self):
        with open(os.path.join(_test_data, 'episodes_list.htm'), mode='rb') as file_:
            episodes = parser._parse_episodes(file_.read())
        self.assertEqual(episodes['prev'], '1')
        self.assertEqual(episodes['next'], '3')
        self.assertEqual(len(episodes['episodes']), 21)
        self.assertEqual(episodes['episodes'][0], {'info': {'genre': u'Adventure, Drama, Mystery, Sci-Fi, Thriller',
                                                            'rating': 7.1},
                                                   'leechers': u'6',
                                                   'seeders': u'29',
                                                   'link': u'http://www.rarbg.to/torrent/z6cms5v',
                                                   'thumb': u'http://dyncdn.me/static/over/122d819bc3a2f7977bae40f47a50aa56b7ab5acf.jpg',
                                                   'title': u'Siberian.Cut.S01E04.Ice.Gauntlet.720p.HDTV.x264-DHD[rartv]',
                                                   'imdb': u'tt2935974',
                                                   'size': u'1.13 GB'})

    def test_parse_episode_with_mediainfo(self):
        with open(os.path.join(_test_data, 'episode_mediainfo.htm'), mode='rb') as file_:
            episode = parser._parse_episode_page(file_.read())
        self.assertEqual(episode, {'seeders': u'50',
                                   'poster': u'http://dyncdn.me/static/20/tvdb/49626db5f32828d79825a1236876b618_banner_optimized.jpg',
                                   'leechers': u'45',
                                   'imdb': u'tt2431438',
                                   'size': u'3.12 GB',
                                   'info': {'plot': u"A group of people around the world are suddenly linked mentally and must find a way to survive being hunted by those who see them as a threat to the world's order.",
                                            'episode': 12,
                                            'title':u'Sense8',
                                            'rating': 7.5,
                                            'season': 1,
                                            'cast': [u'Jamie Clayton', u'Max Riemelt', u'Anupam Kher'],
                                            'genre': u'Drama, Sci-Fi ',
                                            'year': 2015},
                                   'filename': u'Sense8.S01E12.1080p.WEBRip.x264-2HD[rartv]',
                                   'magnet': u'magnet:?xt=urn:btih:78b4d898ffb73ed9f5e4236cdd81250f68c43a5c&dn=Sense8.S01E12.1080p.WEBRip.x264-2HD%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710',
                                   'video': {'duration': 3271,
                                             'width': 1920,
                                             'codec': 'h264',
                                             'aspect': 1.7777777777777777,
                                             'height': 1080},
                                   'audio': {'channels': 6,
                                             'codec': 'ac3',
                                             'language': ''},
                                   'torrent': u'https://www.rarbg.to/download.php?id=528f1ga&f=Sense8.S01E12.1080p.WEBRip.x264-2HD%5Brartv%5D-[rarbg.com].torrent'})

    def test_parse_episode_with_duration_only(self):
        with open(os.path.join(_test_data, 'episode_duration.htm'), mode='rb') as file_:
            episode = parser._parse_episode_page(file_.read())
        self.assertEqual(episode, {'magnet': u'magnet:?xt=urn:btih:6a5aabd24a1f1a728d6a980d338d5378fc11d5c8&dn=Melissa+and+Joey+S04E14+You+Little+Devil+HDTV+x264-FiHTV%5Bettv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710',
                                   'leechers': u'87',
                                   'seeders': u'215',
                                   'info': {'plot': u'After a family scandal leaves Mel a local politician alone with her niece Lennox and nephew Ryder she hires a man named Joe to become the family\'s male nannyor "manny".',
                                            'episode': 14,
                                            'title': u'Melissa & Joey',
                                            'rating': 7.1,
                                            'season': 4,
                                            'cast': [u'Melissa Joan Hart', u'Joseph Lawrence', u'Taylor Spreitler', u'Nick Robinson'],
                                            'genre': u'Comedy ',
                                            'year': 2010},
                                   'imdb': u'tt1597420',
                                   'video': {'duration': 1220},
                                   'poster': u'http://dyncdn.me/static/20/tvdb/019651dd094f0d00183e0106b4c3b380_banner_optimized.jpg',
                                   'size': u'220.82 MB',
                                   'torrent': u'https://www.rarbg.to/download.php?id=d8urtxn&f=Melissa%20and%20Joey%20S04E14%20You%20Little%20Devil%20HDTV%20x264-FiHTV%5Bettv%5D-[rarbg.com].torrent',
                                   'filename': u'Melissa and Joey S04E14 You Little Devil HDTV x264-FiHTV[ettv]'})

    def test_parse_episode_without_mediainfo(self):
        with open(os.path.join(_test_data, 'episode_no_mediainfo.htm'), mode='rb') as file_:
            episode = parser._parse_episode_page(file_.read())
        self.assertEqual(episode, {'magnet': u'magnet:?xt=urn:btih:99ef140a2e7e84d59317f0790ab03fdf292ed3f8&dn=Strike+Back+Legacy+S05E02+HDTV+XviD-FUM%5Bettv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710',
                                   'leechers': u'184',
                                   'seeders': u'426',
                                   'info': {'plot': u"The flashy adventures all over the world of British secret service MI6's dashing special ops team Section 20's fearless hotshots. Scott and Stonebridge eagerlychase Latif the Pakistani Al-Qaeda mastermind behind many terrorist crimes but also other rogue threats to peace.",
                                            'episode': 2,
                                            'title': u'Strike Back',
                                            'rating': 8.3,
                                            'season': 5,
                                            'year': 2010,
                                            'cast': [u'Philip Winchester', u'Sullivan Stapleton', u'Michelle Lukes', u'Rhashan Stone', u'Rhona Mitra'], 'genre': u'Action, Drama, Thriller '},
                                   'imdb': u'tt1492179',
                                   'poster': u'http://dyncdn.me/static/20/tvdb/161b1a612f6d3aecd978e1df9fd48675_banner_optimized.jpg',
                                   'size': u'376.43 MB',
                                   'torrent': u'https://www.rarbg.to/download.php?id=2kdvirg&f=Strike%20Back%20Legacy%20S05E02%20HDTV%20XviD-FUM%5Bettv%5D-[rarbg.com].torrent',
                                   'filename': u'Strike Back Legacy S05E02 HDTV XviD-FUM[ettv]'})


if __name__ == '__main__':
    unittest.main()
