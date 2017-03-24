# coding: utf-8
# Created on: 25.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import sys
import time
import xbmc
from simpleplugin import Addon
from libs.autodownloader import filter_torrents


addon = Addon()
monitor = xbmc.Monitor()
if not addon.enable_autodownload:
    addon.log_warning('Autodownload service is disabled.')
    sys.exit()
started = False
start_time = time.time()
while not monitor.abortRequested():
    if time.time() - start_time > 1800:  # Filter new torrents every 30 minutes
        filter_torrents()
        start_time = time.time()
    if not started:
        addon.log_notice('Autodownload service started.')
        started = True
        filter_torrents()
    xbmc.sleep(250)
addon.log_notice('Autodownload service stopped.')
