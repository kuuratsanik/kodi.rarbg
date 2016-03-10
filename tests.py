#!/usr/bin/env python
# coding: utf-8
# Module: tests
# Created on: 16.02.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
import unittest

basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(basedir, 'tests'))

from tests_utils import *
from tests_tvdb import *
from tests_torrent_info import *
from tests_actions import *

if __name__ == '__main__':
    unittest.main()
