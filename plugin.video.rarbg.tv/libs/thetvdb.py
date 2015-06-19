# -*- coding: utf-8 -*-
# Module: thetvdb
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xml.etree.ElementTree as et
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
    root = et.fromstring(load_page(_GET_BY_ID, data={'imdbid' : imdbid}).encode('utf-8'))
    series = root.find('Series')
    if series is not None:
        return {'tvshowtitle': series.find('SeriesName').text,
                'plot': series.find('Overview').text,
                'premiered': series.find('FirstAired').text,
                'banner': _GRAPHICS + series.find('banner').text}
    else:
        return None
