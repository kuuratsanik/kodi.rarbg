# -*- coding: utf-8 -*-
# Module: parser
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# Rarbg API docs: http://torrentapi.org/apidocs_v2.txt

from webclient import load_page

_API = 'https://torrentapi.org/pubapi_v2.php'


def get_token():
    """
    Get a token to access Rarbg API
    The token will expire in 15 min
    :return:
    """
    data = {'get_token': 'get_token'}
    return load_page(_API, data=data, headers={'content-type': 'application/json'})['token']


def get_torrents(token, **kwargs):
    """
    Get the list of recent TV episode torrents with extended data
    :param token: str - Rarbg API token
    :param kwargs: dict - keyword Rarbg API parameters
    :return: list - the list of torrents
    """
    data = {'token': token, 'format': 'json_extended'}
    data.update(kwargs)
    try:
        return load_page(_API, data=data, headers={'content-type': 'application/json'})['torrent_results']
    except KeyError:
        return []
