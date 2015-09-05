# -*- coding: utf-8 -*-
# Module: thetvdb
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Get info from TheTVDB"""

import xml.etree.ElementTree as etree
from webclient import load_page

_GET_SERIES = 'http://thetvdb.com/api/41277F23AA12DE38/series/{id}/en.xml'
_GET_EPISODE = 'http://thetvdb.com/api/41277F23AA12DE38/series/{id}/default/{season}/{episode}/en.xml'
_SEARCH_SERIES = 'http://thetvdb.com/api/GetSeries.php'
_GET_BY_ID = 'http://thetvdb.com/api/GetSeriesByRemoteID.php'
_GRAPHICS = 'http://thetvdb.com/banners/'


def get_series(thetvdb_id):
    """
    Get series info by TheTVDB ID

    :param thetvdb_id: str
    :return:
    """
    page = load_page(_GET_SERIES.format(id=thetvdb_id)).encode('utf-8', 'replace')
    if 'Not Found' in page:
        return None
    root = etree.fromstring(page)
    series = root.find('Series')
    if series is not None:
        poster = series.find('poster').text if series.find('poster') is not None else None
        banner = series.find('banner').text if series.find('banner') is not None else None
        fanart = series.find('fanart').text if series.find('fanart') is not None else None
        return {'tvshowtitle': series.find('SeriesName').text,
                'plot': series.find('Overview').text,
                'genre': series.find('Genre').text,
                'premiered': series.find('FirstAired').text,
                'poster': _GRAPHICS + poster if poster else None,
                'banner': _GRAPHICS + banner if banner else None,
                'fanart': _GRAPHICS + fanart if fanart else None}
    else:
        return None


def get_episode(thetvdb_id, season, episode):
    """
    Get episode info

    :param thetvdb_id: str
    :param season: str
    :param episode: str
    :return:
    """
    page = load_page(_GET_EPISODE.format(id=thetvdb_id, season=season.lstrip('0'),
                                         episode=episode.lstrip('0'))).encode('utf-8', 'replace')
    if 'Not Found' in page:
        return None
    root = etree.fromstring(page)
    ep_info = root.find('Episode')
    if ep_info is not None:
        thumb = ep_info.find('filename').text if ep_info.find('filename') is not None else None
        return {'episode_name': ep_info.find('EpisodeName').text,
                'plot': ep_info.find('Overview').text if ep_info.find('Overview') is not None else '',
                'premiered': ep_info.find('FirstAired').text if ep_info.find('FirstAired') is not None else None,
                'thumb': _GRAPHICS + thumb if thumb else None,
                'director': ep_info.find('Director').text if ep_info.find('Director') is not None else None}
    else:
        return None


def get_series_by_imdbid(imdbid):
    """
    Get basic TV show info from TheTVDB

    :param imdbid:
    :return:
    """
    root = etree.fromstring(load_page(_GET_BY_ID, data={'imdbid' : imdbid}).encode('utf-8'))
    series = root.find('Series')
    if series is not None:
        return {'tvshowtitle': series.find('SeriesName').text,
                'plot': series.find('Overview').text,
                'premiered': series.find('FirstAired').text,
                'banner': _GRAPHICS + series.find('banner').text if series.find('banner') is not None else None}
    else:
        return None


def search_series(seriesname):
    """
    Search TV series on TheTVDB

    :param series_name:
    :return:
    """
    root = etree.fromstring(load_page(_SEARCH_SERIES, data={'seriesname' : seriesname}).encode('utf-8'))
    series = root.findall('Series')
    listing = []
    if series is not None:
        for show in series:
            if show.find('IMDB_ID') is not None:
                listing.append(
                    {'tvshowtitle': show.find('SeriesName').text,
                     'imdb': show.find('IMDB_ID').text,
                     'banner': _GRAPHICS + show.find('banner').text if show.find('banner') is not None else None})
    return listing

