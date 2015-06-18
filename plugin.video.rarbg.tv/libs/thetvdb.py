# -*- coding: utf-8 -*-
# Module: thetvdb
# Author: Roman V.M.
# Created on: 17.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from xml.dom.minidom import parseString
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
    document = parseString(load_page(_GET_BY_ID, data={'imdbid' : imdbid}))
    try:
        return {'tvshowtitle': document.getElementsByTagName('SeriesName')[0].firstChild.nodeValue,
                'plotoutline': document.getElementsByTagName('Overview')[0].firstChild.nodeValue,
                'premiered': document.getElementsByTagName('FirstAired')[0].firstChild.nodeValue,
                'banner': _GRAPHICS + document.getElementsByTagName('banner')[0].firstChild.nodeValue}
    except IndexError:
        return {}
