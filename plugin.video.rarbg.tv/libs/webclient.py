# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
import urllib2
import socket
import zlib
import cPickle as pickle
from datetime import datetime, timedelta
from urlparse import urlsplit
import xbmc
from addon import Addon

__addon__ = Addon()
cache_file = os.path.join(xbmc.translatePath('special://profile/addon_data/').decode('utf-8'),
                          __addon__.id,
                          'cache.pcl')


class Cache(object):
    """Cache decorator"""
    def __init__(self, func):
        self.func = func
        self.cache = {}
        if os.path.exists(cache_file):
            mode = 'r+b'
        else:
            mode = 'w+b'
        self.cache_file = open(cache_file, mode=mode)
        try:
            self.cache = pickle.load(self.cache_file)
        except (EOFError, pickle.UnpicklingError):
            pass

    def __call__(self, url, post_data=None):
        """Decorator call"""
        current_time = datetime.now()
        try:
            compr_page, timestamp = self.cache[url]
            page = zlib.decompress(compr_page)
            if current_time - timestamp > timedelta(minutes=15):
                raise KeyError
        except KeyError:
            page = self.func(url, post_data)
            if page != '404':
                self.cache[url] = (zlib.compress(page), current_time)
            self.cache_file.seek(0)
            pickle.dump(self.cache, self.cache_file)
            self.cache_file.truncate()
        self.cache_file.close()
        return page


def load_page(url, post_data=None):
    """
    Web-client
    """
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
    return page
