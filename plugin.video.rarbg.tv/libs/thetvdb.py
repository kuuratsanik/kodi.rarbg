# -*- coding: utf-8 -*-
# Module: thetvdb
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Get info from TheTVDB"""

import xml.etree.ElementTree as etree
from webclient import load_page

_GET_SERIES = 'http://thetvdb.com/api/GetSeries.php'
_GET_BY_ID = 'http://thetvdb.com/api/GetSeriesByRemoteID.php'
_GRAPHICS = 'http://thetvdb.com/banners/'


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


def get_series(seriesname):
    """
    Search TV series on TheTVDB

    :param series_name:
    :return:
    """
    root = etree.fromstring(load_page(_GET_SERIES, data={'seriesname' : seriesname}).encode('utf-8'))
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
