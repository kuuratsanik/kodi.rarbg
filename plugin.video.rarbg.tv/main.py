# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from base64 import urlsafe_b64decode
from urlparse import parse_qs
from xbmcplugin import setContent
from libs import views

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
setContent(__handle__, 'tvshows')


def plugin_root():
    """
    Plugin root
    :return:
    """
    views.root_view(__url__, __handle__)


def episode_list(page):
    """
    The list of episode releases by most recent first
    :return:
    """
    views.episode_list_view(__url__, __handle__, page)


def episode_page(encoded_url):
    """
    Episode page
    :param encoded_url:
    :return:
    """
    views.episode_view(__handle__, urlsafe_b64decode(encoded_url))


def router(paramstring):
    """
    Plugin router function
    :param paramstring: str
    :return:
    """
    params = parse_qs(paramstring)
    if params:
        if params['action'][0] == 'episode_list':
            episode_list(params['page'][0])
        if params['action'][0] == 'episode':
            episode_page(params['url'][0])
    else:
        plugin_root()


if __name__ == '__main__':
    router(sys.argv[2][1:])
