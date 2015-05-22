# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import re
#
import requests
#
from xbmc import LOGDEBUG, LOGERROR
#
from addon import Addon
from dialog import Dialog

__addon__ = Addon()


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


def anti_captcha(*args, **kwargs):
    """
    Anticaptcha function

    It wraps load_page and checks if rarbg.to site returns captcha.
    :param args:
    :param kwargs:
    :return:
    """
    page = load_page(*args, **kwargs)
    if re.search(r'Prove that you are a human by solving the captcha below', page) is not None:
        __addon__.log('The site returned captcha!', LOGERROR)
        while True:
            captcha_match = re.search(r'<img src="(/captcha2/(.+?)\.png)" />', page)
            __addon__.log('Captcha: {0}'.format(captcha_match.group(1)))
            dialog = Dialog('http://www.rarbg.to' + captcha_match.group(1))
            dialog.doModal()
            if dialog.confirmed:
                post_data = {'solve_string': dialog.text,
                             'captcha_id': captcha_match.group(2),
                             'submitted_bot_captcha': '1'}
                page = load_page('http://www.rarbg.to/bot_check.php', method='post', data=post_data)
                if re.search(r'You have been successfully verified as a human', page) is not None:
                    __addon__.log('Captcha solved successfully!')
                    page = load_page(*args, **kwargs)
                    break
                else:
                    __addon__.log('Unable to solve the captcha!', LOGERROR)
                    page = load_page(*args, **kwargs)
                    continue
            else:
                __addon__.log('Solving captcha is cancelled.')
                page = ''
                break
    return page
