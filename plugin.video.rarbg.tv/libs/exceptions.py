# coding: utf-8
# Module: exceptions
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)


class RarbgError(Exception):
    """Base exception class"""
    pass


class Http404Error(RarbgError):
    """Excepiton if a web-page is not found"""
    pass


class NoDataError(RarbgError):
    """Exception if a request to TheTVDB returned no valid data"""
    pass
