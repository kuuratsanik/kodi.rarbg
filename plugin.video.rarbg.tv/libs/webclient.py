# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import urllib2
import socket
import zlib
from urlparse import urlsplit
#
from xbmc import LOGDEBUG
#
from addon import Addon

__addon__ = Addon()


def load_page(url, post_data=None):
    """
    Web-client

    post_data - URL-encoded data for POST request
    :param url: str
    :param post_data: str
    """
    __addon__.log(url)
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0',
                'Host': urlsplit(url).hostname,
                'Accept-Charset': 'UTF-8',
                'Accept': 'text/html',
                'Accept-Language': 'en-US, en',
                'Accept-Encoding': 'gzip, deflate'}
    request = urllib2.Request(url, None, headers)
    try:
        session = urllib2.urlopen(request, post_data)
    except (urllib2.URLError, socket.timeout):
        page = '404'
    else:
        page = session.read()
        if session.info().getheader('Content-Encoding', '') == 'gzip':
            page = zlib.decompress(page, zlib.MAX_WBITS + 16)
        elif session.info().getheader('Content-Encoding', '') == 'deflate':
            page = zlib.decompress(page, -zlib.MAX_WBITS)
        session.close()
    __addon__.log(page, LOGDEBUG)
    return page
