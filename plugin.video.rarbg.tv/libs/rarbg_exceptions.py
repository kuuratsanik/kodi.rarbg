# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua


class RarbgError(Exception):
    pass


class Http404Error(RarbgError):
    pass


class TvdbError(RarbgError):
    pass


class RarbgApiError(RarbgError):
    pass
