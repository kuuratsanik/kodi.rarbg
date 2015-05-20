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
import requests
#
from xbmc import LOGDEBUG
#
from addon import Addon

__addon__ = Addon()

def __depreciated__():
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


def load_page(url, method='get', data=None):
    """
    Web-client

    :param url: str - URL
    :param method: str - 'get' or 'post' methdos, other methods are not supported.
    :param data: dict - data to be sent to a server
    :return:
    """
    __addon__.log('URL: {0}'.format(url))
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0',
                'Accept-Charset': 'UTF-8',
                'Accept': 'text/html',
                'Accept-Language': 'en-US, en',
                'Accept-Encoding': 'gzip, deflate'}
    if method == 'get':
        response = requests.get(url, params=data, headers=headers, verify=False)
    elif method == 'post':
        response = requests.post(url, data=data, headers=headers, verify=False)
    else:
        raise RuntimeError('Invalid load_page method!')
    page = response.text
    __addon__.log(page, LOGDEBUG)
    return page
