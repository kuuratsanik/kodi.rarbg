# coding: utf-8
# Module: fanarttv
# Created on: 04.09.2015
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua


from webclient import load_page

APIKEY = 'd4a012636b8121a5f5e2ebcacae5500e'
URL = 'http://webservice.fanart.tv/v3/tv/{0}'


def get_art(thetvdb_id):
    """
    Get TV show art from fanart.tv

    @param thetvdb_id:
    @return:
    """
    return load_page(URL.format(thetvdb_id), data={'api_key': APIKEY}, headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    print get_art('196841')
