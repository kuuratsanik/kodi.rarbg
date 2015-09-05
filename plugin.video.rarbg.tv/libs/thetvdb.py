# -*- coding: utf-8 -*-
# Module: thetvdb
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Get info from TheTVDB"""

import xml.etree.ElementTree as etree
from webclient import load_page

_APIKEY = '41277F23AA12DE38'
_GET_SERIES = 'http://thetvdb.com/api/{apikey}/series/{id}/en.xml'
_GET_EPISODE = 'http://thetvdb.com/api/{apikey}/series/{id}/default/{season}/{episode}/en.xml'
_SEARCH_SERIES = 'http://thetvdb.com/api/GetSeries.php'
_GET_BY_ID = 'http://thetvdb.com/api/GetSeriesByRemoteID.php'
_GRAPHICS = 'http://thetvdb.com/banners/'


def _parse_items(parent):
    """
    Return all content from 'parent' section of element tree as a dict
    
    @param parent: etree node
    @return:
    """
    data = {}
    for child in parent:
        if child.tag in ('poster', 'banner', 'fanart') and child.text is not None:
                data[child.tag] = _GRAPHICS + child.text
        else:
            data[child.tag] = child.text
    return data


def get_series(thetvdb_id):
    """
    Get series info by TheTVDB ID

    @param thetvdb_id: str
    @return:
    """
    page = load_page(_GET_SERIES.format(apikey=_APIKEY, id=thetvdb_id)).encode('utf-8', 'replace')
    if 'Not Found' in page:
        return None
    root = etree.fromstring(page)
    series = root.find('Series')
    if series is not None:
        return _parse_items(series)
    else:
        return None


def get_episode(thetvdb_id, season, episode):
    """
    Get episode info

    @param thetvdb_id: str
    @param season: str
    @param episode: str
    @return:
    """
    page = load_page(_GET_EPISODE.format(apikey=_APIKEY, id=thetvdb_id,
                                         season=season.lstrip('0'),
                                         episode=episode.lstrip('0'))).encode('utf-8', 'replace')
    if 'Not Found' in page:
        return None
    root = etree.fromstring(page)
    ep_info = root.find('Episode')
    if ep_info is not None:
        return _parse_items(ep_info)
    else:
        return None


def get_series_by_imdbid(imdbid):
    """
    Get basic TV show info from TheTVDB

    @param imdbid:
    @return:
    """
    root = etree.fromstring(load_page(_GET_BY_ID, data={'imdbid' : imdbid}).encode('utf-8', 'replace'))
    series = root.find('Series')
    if series is not None:
        return _parse_items(series)
    else:
        return None


def search_series(seriesname):
    """
    Search TV series on TheTVDB

    @param seriesname:
    @param:
    """
    root = etree.fromstring(load_page(_SEARCH_SERIES, data={'seriesname': seriesname}).encode('utf-8', 'replace'))
    series = root.findall('Series')
    listing = []
    if series is not None:
        for show in series:
            if show.find('IMDB_ID') is not None:
                listing.append(_parse_items(show))
    return listing

