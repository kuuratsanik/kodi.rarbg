# -*- coding: utf-8 -*-
# Module: parser
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# Rarbg API docs: http://torrentapi.org/apidocs_v2.txt
"""Get torrent info from Rarbg API"""

"""
Link:
http://torrentapi.org/pubapi_v2.php?mode=list&category=18;41&format=json_extended&token=xxxxxx

Examples of torrent data:
--------------------
category: TV HD Episodes
seeders: 50
pubdate: 2015-06-16 06:46:20 +0000
title: Game.of.Thrones.S05E08.Hardhome.720p.WEB-DL.DD5.1.H.264-NTb[rartv]
episode_info: {u'airdate': u'2015-05-31', u'tvdb': u'121361', u'title': u'Hardhome', u'epnum': u'08', u'seasonnum': u'5',
    u'imdb': u'tt0944947', u'tvrage': u'24493'}
leechers: 28
ranked: 1
info_page: https://torrentapi.org/redirect_to_info.php?token=3z5vme4n97&p=8_7_0_3_3_5__a484c51af8
download: magnet:?xt=urn:btih:a484c51af81ae48a9dad4fbb0c4186956c7013ff&dn=Game.of.Thrones.S05E08.Hardhome.720p.WEB-DL.DD5.1.H.264-NTb%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce
size: 1973983675
----------------------
category: TV HD Episodes
seeders: 13
pubdate: 2015-01-30 19:27:52 +0000
title: Game.of.Thrones.S04.1080p.BluRay.x264-ROVERS[rartv]
episode_info: {u'tvdb': u'121361', u'tvrage': u'24493', u'imdb': u'tt0944947'}
leechers: 42
ranked: 1
info_page: https://torrentapi.org/redirect_to_info.php?token=3z5vme4n97&p=7_8_3_5_6_1__d9678293e0
download: magnet:?xt=urn:btih:d9678293e0980dcac8d054394444afd1f467ee48&dn=Game.of.Thrones.S04.1080p.BluRay.x264-ROVERS%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce
size: 45082604600
"""

from xbmc import LOGERROR
from simpleplugin import Plugin
from utilities import load_page
from exceptions import NoDataError

_API = 'http://torrentapi.org/pubapi_v2.php'
_plugin = Plugin()


@_plugin.cached()
def _get_token():
    """
    Get a token to access Rarbg API

    The token will expire in 15 min
    :return:
    """
    data = {'get_token': 'get_token'}
    return load_page(_API, data=data, headers={'content-type': 'application/json'})['token']


def get_torrents(params):
    """
    Get the list of recent TV episode torrents with extended data

    :param params: dict - Rarbg API query params
    :return: list - the list of torrents
    :raises: libs.exceptions.NoDataError if Rarbg returns no torrent data
    """
    params['token'] = _get_token()
    params['format'] = 'json_extended'
    try:
        return load_page(_API, data=params, headers={'content-type': 'application/json'})['torrent_results']
    except KeyError:
        raise NoDataError
