# coding: utf-8
# Module: utilities
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import requests
from xbmc import LOGERROR
from simpleplugin import Plugin
from exceptions import Http404Error

__all__ = ['ThreadPool', 'load_page']

HEADERS = (
    ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'),
    ('Accept-Charset', 'UTF-8'),
    ('Accept', 'text/html,text/plain,application/json,application/xml'),
    ('Accept-Language', 'en-US, en'),
    ('Accept-Encoding', 'gzip, deflate'),
)
plugin = Plugin()


def load_page(url, params=None, headers=None):
    """
    Web-client

    Loads web-pages via GET requests with optional query string data

    :param url: the URL of a web-page to be loaded
    :type url: str
    :param params: parameters to be sent to a server in a URL-encoded paramstring
    :type params: dict
    :param headers: additional headers for a HTTP request
    :type headers: dict
    :return: response contents or a dictionary of json-decoded data
    :rtype: dict -- for JSON response
    :rtype: str -- for other types of responses
    :raises: libs.exceptions.Http404Error -- if 404 error if returned
    """
    request_headers = dict(HEADERS)
    plugin.log('URL: {0}, params: {1}'.format(url, str(params)))
    if headers is not None:
        request_headers.update(headers)
    response = requests.get(url, params=params, headers=request_headers, verify=False)
    if response.status_code == 404:
        message = 'URL {0} with params {1} not found.'.format(url, str(params))
        plugin.log(message, LOGERROR)
        raise Http404Error(message)
    if 'application/json' in response.headers['content-type']:
        contents = response.json()
    else:
        contents = response.text
    plugin.log(response.text.encode('utf-8'))
    return contents
