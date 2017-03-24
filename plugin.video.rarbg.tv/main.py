# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""The Main Plugin Module"""

from simpleplugin import debug_exception
from libs.actions import plugin

with debug_exception(plugin.log_error):
    plugin.run()

