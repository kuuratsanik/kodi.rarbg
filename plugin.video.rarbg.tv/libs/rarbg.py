# -*- coding: utf-8 -*-
# Module: parser
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# Rarbg API docs: http://torrentapi.org/apidocs_v2.txt

from simpleplugin import Plugin
from webclient import load_page

_API = 'https://torrentapi.org/pubapi_v2.php'
_plugin = Plugin()


@_plugin.cached(15)
def get_token():
    """
    Get a token to access Rarbg API
    The token will expire in 15 mins
    :return:
    """
    return load_page(_API, data={'get_token': 'get_token'}, headers={'content-type': 'application/json'})['token']
