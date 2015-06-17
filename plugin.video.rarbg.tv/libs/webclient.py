# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import urlparse
import requests
from xbmc import LOGDEBUG
from simpleplugin import Plugin

_plugin = Plugin()


def load_page(url, method='get', data=None, headers=None):
    """
    Web-client

    :param url: str - URL
    :param method: str - 'get' or 'post' methdos, other methods are not supported.
    :param data: dict - data to be sent to a server
    :param headers: dict - custom headers to replace/add to default ones
    :return: unicode or dict - response contents or a dictionary of json-decoded data
    """
    _plugin.log('URL: {0}'.format(url))
    request_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0',
                       'Accept-Charset': 'UTF-8',
                       'Accept': 'text/html,application/json,application/xml',
                       'Accept-Language': 'en-US, en',
                       'Accept-Encoding': 'gzip, deflate'}
    if headers is not None:
        for key, value in headers.iteritems():
            request_headers[key] = value
    contents = None
    with _plugin.get_storage('cookies.pcl') as cookie_jar:
        cookies = cookie_jar.get(urlparse.urlparse(url).hostname)
        if method == 'get':
            response = requests.get(url, params=data, headers=request_headers, verify=False, cookies=cookies)
        elif method == 'post':
            response = requests.post(url, data=data, headers=request_headers, verify=False, cookies=cookies)
        else:
            raise RuntimeError('Invalid load_page method!')
        cookie_jar[urlparse.urlparse(url).hostname] = response.cookies.get_dict()
        if response.headers['content-type'] == 'application/json':
            contents = response.json()
        else:
            contents = response.text
        _plugin.log(response.text, LOGDEBUG)
    return contents
