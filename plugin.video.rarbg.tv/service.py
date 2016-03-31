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
started = False
start_time = time.time()
while not xbmc.abortRequested:
    if time.time() - start_time > 1800:  # Filter new torrents every 30 minutes
        filter_torrents()
        start_time = time.time()
    if not started:
        addon.log('Autodownload service started.', xbmc.LOGNOTICE)
        started = True
    xbmc.sleep(250)
addon.log('Autodownload service stopped.', xbmc.LOGNOTICE)
