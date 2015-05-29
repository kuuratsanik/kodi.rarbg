# -*- coding: utf-8 -*-
# Module: test_template
# Author: Roman V.M.
# Created on: 27.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

__id__ = 'plugin.video.rarbg.tv'
__script__ = 'main'
__start_point__ = 'router'

import sys
import os
import mock
from plugin_test import plugin, import_mock

plugin.sys_argv = ['plugin://{0}/'.format(__id__), '1', '']
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), __id__))


class FakeDialog(object):
    def __init__(self, captcha=''):
        self._captcha = captcha
        self.text = ''
        self.confirmed = True

    def doModal(self):
        print 'Captcha image:'
        print self._captcha
        self.text = raw_input('Enter text on the picture: ')


@mock.patch('sys.argv', plugin.sys_argv)
@mock.patch('__builtin__.__import__', side_effect=import_mock)
# Addon-specific patches
@mock.patch('libs.dialog.Dialog', side_effect=FakeDialog)
@mock.patch('xbmc.Keyboard')
@mock.patch('libs.addon.Addon')
def main(mock_Addon, mock_Keyboard, *args):
    # Set-up testing environment
    mock_addon = mock_Addon.return_value
    mock_addon.id = __id__
    mock_addon.addon_dir = os.path.dirname(__file__)
    mock_addon.config_dir = os.path.dirname(__file__)
    mock_addon.icons_dir = '/icons'
    mock_addon.quality = ['18']
    mock_keyboard = mock_Keyboard.return_value
    mock_keyboard.isConfirmed.return_value = True
    mock_keyboard.getText.return_value = 'Castle'
    # Start testing
    script = __import__(__script__)
    while plugin.sys_argv:
        getattr(script, __start_point__)(plugin.sys_argv[2])


if __name__ == '__main__':
    main()
