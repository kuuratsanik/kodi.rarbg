# coding: utf-8
# Created on: 25.03.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import time
import xbmc
from libs.autodownloader import filter_torrents

start_time = time.time()
while not xbmc.abortRequested:
    if time.time() - start_time > 1800:
        filter_torrents()
        start_time = time.time()
    xbmc.sleep(250)
