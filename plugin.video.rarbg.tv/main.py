# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urlparse import parse_qs
from libs import views

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])


def plugin_root():
    """
    Plugin root
    :return:
    """
    views.root_view(__url__, __handle__)


def episode_list():
    """
    The list of episode releases by most recent first
    :return:
    """
    views.episode_list_view(__url__, __handle__)


def router(paramstring):
    """
    Plugin router function
    :param paramstring: str
    :return:
    """
    params = parse_qs(paramstring)
    if params:
        if params['action'][0] == 'episode_list':
            episode_list()
    else:
        plugin_root()


if __name__ == '__main__':
    router(sys.argv[2][1:])
