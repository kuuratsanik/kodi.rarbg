# -*- coding: utf-8 -*-
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Get info from TheTVDB"""

import xml.etree.ElementTree as etree
from utilities import load_page
from exceptions import NoDataError

_APIKEY = '41277F23AA12DE38'
_GET_SERIES = 'http://thetvdb.com/api/{apikey}/series/{id}/en.xml'
_GET_EPISODE = 'http://thetvdb.com/api/{apikey}/series/{id}/default/{season}/{episode}/en.xml'
_SEARCH_SERIES = 'http://thetvdb.com/api/GetSeries.php'
_GET_BY_ID = 'http://thetvdb.com/api/GetSeriesByRemoteID.php'
_GRAPHICS = 'http://thetvdb.com/banners/'


def _parse_items(parent):
    """
    Return all content from 'parent' section of element tree as a dict
    
    :param parent: etree node
    :return:
    """
    data = {}
    for child in parent:
        if child.tag in ('poster', 'banner', 'fanart', 'filename') and child.text is not None:
                data[child.tag] = _GRAPHICS + child.text
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
    :raises: libs.exceptions.NoDataError if TheTVDB returns empty XML
    """
    page = load_page(_GET_SERIES.format(apikey=_APIKEY, id=tvdbid)).encode('utf-8', 'replace')
    root = etree.fromstring(page)
    series = root.find('Series')
    if series is None:
        raise NoDataError('TheTVDB has no valid data for ID {0}!'.format(tvdbid))
    else:
        return _parse_items(series)


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
    :raises: libs.exceptions.NoDataError if TheTVDB returns empty XML
    """
    page = load_page(_GET_EPISODE.format(apikey=_APIKEY, id=tvdbid,
                                         season=season.lstrip('0'),
                                         episode=episode.lstrip('0'))).encode('utf-8', 'replace')
    root = etree.fromstring(page)
    ep_info = root.find('Episode')
    if ep_info is None:
        raise NoDataError('TheTVDB has no valid data for episode {0} - S{1}E{2}!'.format(tvdbid,
                                                                                         season,
                                                                                         episode))
    else:
        return _parse_items(ep_info)


def search_series(seriesname):
    """
    Search TV series on TheTVDB

    :param seriesname: a string to search at TheTVDB
    :type seriesname: str
    :return: the list of found TV series data as dicts
    :rtype: list
    :raises: libs.exceptions.NoDataError if TheTVDB returns empty XML
    """
    root = etree.fromstring(load_page(_SEARCH_SERIES, data={'seriesname': seriesname}).encode('utf-8', 'replace'))
    series = root.findall('Series')
    if series:
        listing = []
        for show in series:
            if show.find('IMDB_ID') is not None:
                listing.append(_parse_items(show))
        return listing
    else:
        raise NoDataError
