# coding: utf-8
# Created on: 25.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import sys
import time
import xbmc
from simpleplugin import Addon
from libs.autodownloader import filter_torrents


addon = Addon()
if not addon.enable_autodownload:
    addon.log('Autodownload service is disabled.', xbmc.LOGWARNING)
    sys.exit()
start_time = time.time()
while not xbmc.abortRequested:
    if time.time() - start_time > 1800:  # Filter new torrents every 30 minutes
        torrents_found = filter_torrents()
        if torrents_found:
            xbmc.executebuiltin('UpdateLibrary(video)')
        start_time = time.time()
    xbmc.sleep(250)
