# -*- coding: utf-8 -*-
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Get info from TheTVDB"""

from simpleplugin import Plugin
from web_client import load_page, Http404Error

plugin = Plugin('plugin.video.rarbg.tv')

import xml.etree.cElementTree as etree
try:
    etree.fromstring('<?xml version="1.0"?><foo><bar/></foo>')
except TypeError:
    plugin.log_warning('cElementTree is not available! Falling back to ElementTree.')
    import xml.etree.ElementTree as etree

__all__ = ['get_series', 'get_episode', 'search_series']

APIKEY = '41277F23AA12DE38'
GET_SERIES = 'http://thetvdb.com/api/{apikey}/series/{id}/en.xml'
GET_EPISODE = 'http://thetvdb.com/api/{apikey}/series/{id}/default/{season}/{episode}/en.xml'
SEARCH_SERIES = 'http://thetvdb.com/api/GetSeries.php'
GET_BY_ID = 'http://thetvdb.com/api/GetSeriesByRemoteID.php'
GRAPHICS = 'http://thetvdb.com/banners/'


class TvdbError(Exception):
    pass


def parse_items(parent):
    """
    Return all content from the 'parent' section of an XML element tree as a dict
    
    :param parent: etree node
    :return: a dict with parsed data
    :rtype: dict
    """
    data = {}
    for child in parent:
        if child.tag in ('poster', 'banner', 'fanart', 'filename') and child.text is not None:
                data[child.tag] = GRAPHICS + child.text
        else:
            data[child.tag] = child.text or ''
    return data


def get_series(tvdbid):
    """
    Get series info by TheTVDB ID

    :param tvdbid: series ID on TheTVDB
    :type tvdbid: str
    :return: TV series data
    :rtype: dict
    :raises TvdbError: if TheTVDB returns no data
    """
    try:
        page = load_page(GET_SERIES.format(apikey=APIKEY, id=tvdbid))
    except Http404Error:
        raise TvdbError('TheTVDB returned 404 page!')
    root = etree.fromstring(page)
    series = root.find('Series')
    if series is None:
        raise TvdbError('TheTVDB returned invalid XML data!')
    else:
        return parse_items(series)


def get_episode(tvdbid, season, episode):
    """
    Get episode info

    :param tvdbid: TVDB series ID
    :type tvdbid: str
    :param season: season # without preceding 0
    :type season: str
    :param episode: episode # without preceding 0
    :type episode: str
    :return: TV episode data
    :rtype: dict
    :raises TvdbError: if TheTVDB returns no data
    """
    try:
        page = load_page(GET_EPISODE.format(apikey=APIKEY, id=tvdbid,
                                            season=season.lstrip('0'),
                                            episode=episode.lstrip('0')))
    except Http404Error:
        raise TvdbError('TheTVDB returned 404 page!')
    root = etree.fromstring(page)
    ep_info = root.find('Episode')
    if ep_info is None:
        raise TvdbError('TheTVDB returned invalid XML data!')
    else:
        return parse_items(ep_info)
