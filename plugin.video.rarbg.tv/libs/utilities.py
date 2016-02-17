# coding: utf-8
# Module: utilities
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import time
import threading
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


class ThreadPool(object):
    """
    Thread pool class

    It creates a pool of worker threads to be run in parallel.
    """
    daemon_threads = True  #: Daemon threads
    thread_count = 4  #: The max. number of active threads

    def __init__(self):
        self._pool = [None] * self.thread_count

    def put(self, func, *args, **kwargs):
        """
        Put a function into the thread pool

        If all available threads are busy, the call will block
        until one of the active threads finishes.

        :param func: a callable object
        :param args: callable's positional arguments
        :param kwargs: callable's keyword arguments
        """
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = self.daemon_threads
        slot = self._get_free_slot()
        thread.start()
        self._pool[slot] = thread

    def _get_free_slot(self):
        while True:
            slot = -1
            for i, thread in enumerate(self._pool):
                if self._pool[i] is None or not thread.is_alive():
                    slot = i
                    break
            if slot >= 0:
                return slot
            time.sleep(0.1)

    def is_all_finished(self):
        """
        Check if there are no more active threads

        :return: ``True`` if there are no active threads
        :rtype: bool
        """
        for thread in self._pool:
            if thread is not None and thread.is_alive():
                return False
        return True


def load_page(url, data=None, headers=None):
    """
    Web-client

    Loads web-pages via GET requests with optional query string data

    :param url: the URL of a web-page to be loaded
    :type url: str
    :param data: data to be sent to a server in a URL query string
    :type data: dict
    :param headers: additional headers for a HTTP request
    :type headers: dict
    :return: response contents or a dictionary of json-decoded data
    :rtype: dict -- for JSON response
    :rtype: str -- for other types of responses
    :raises: libs.exceptions.Http404Error -- if 404 error if returned
    """
    request_headers = dict(HEADERS)
    plugin.log('URL: {0}, params: {1}'.format(url, str(data)))
    if headers is not None:
        request_headers.update(headers)
    response = requests.get(url, params=data, headers=request_headers, verify=False)
    if response.status_code == 404:
        message = 'URL {0} with params {1} not found.'.format(url, str(data))
        plugin.log(message, LOGERROR)
        raise Http404Error(message)
    if 'application/json' in response.headers['content-type']:
        contents = response.json()
    else:
        contents = response.text
    plugin.log(response.text.encode('utf-8'))
    return contents
