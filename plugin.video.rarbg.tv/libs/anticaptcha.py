# -*- coding: utf-8 -*-
# Module: anticaptcha
# Author: Roman V.M.
# Created on: 20.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import re
import pyxbmct.addonwindow as pyxbmct
#
from xbmc import LOGERROR
#
from addon import Addon

__addon__ = Addon()


class _Dialog(pyxbmct.AddonDialogWindow):
    def __init__(self, captcha=''):
        super(_Dialog, self).__init__()
        self.setGeometry(400, 250, 4, 2)
        self.setWindowTitle('Rarbg bot check!')
        self._confirmed = False
        self._set_controls(captcha)
        self._set_navigation()
        self.setFocus(self._edit)

    def _set_controls(self, captcha):
        label = pyxbmct.Label('Enter text on the picture:', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(label, 0, 0, columnspan=2)
        self._image = pyxbmct.Image(captcha)
        self.placeControl(self._image, 1, 0, rowspan=2)
        self._edit = pyxbmct.Edit('')
        self.placeControl(self._edit, 2, 1)
        self._cancel_button = pyxbmct.Button('Cancel')
        self.connect(self._cancel_button, self.close)
        self.placeControl(self._cancel_button, 3, 0)
        self._ok_button = pyxbmct.Button('OK')
        self.placeControl(self._ok_button, 3, 1)
        self.connect(self._ok_button, self._ok)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def _set_navigation(self):
        self._edit.controlUp(self._ok_button)
        self._edit.controlDown(self._ok_button)
        self._cancel_button.setNavigation(self._edit, self._edit, self._ok_button, self._ok_button)
        self._ok_button.setNavigation(self._edit, self._edit, self._cancel_button, self._cancel_button)

    def _ok(self):
        self._confirmed = True
        super(_Dialog, self).close()

    def close(self):
        self._confirmed = False
        super(_Dialog, self).close()

    def set_captcha(self, image):
        self._image.setImage(image)

    @property
    def confirmed(self):
        return self._confirmed

    @property
    def text(self):
        return self._edit.getText()


def anticaptcha(load_page):
    """
    Anticaptcha decorator
    :param load_page: load_page function
    :return:
    """
    def wrapper(*args, **kwargs):
        page = load_page(*args, **kwargs)
        if re.search(r'Prove that you are a human by solving the captcha below', page) is not None:
            __addon__.log('The site returned captcha!', LOGERROR)
            while True:
                captcha_match = re.search(r'<img src="(/captcha2/(.+?)\.png)" />', page)
                __addon__.log('Captcha: {0}'.format(captcha_match.group(1)))
                dialog = _Dialog('http://www.rarbg.to' + captcha_match.group(1))
                dialog.doModal()
                if dialog.confirmed:
                    post_data = {'solve_string': dialog.text,
                                 'captcha_id': captcha_match.group(2),
                                 'submitted_bot_captcha': '1'}
                    page = load_page('http://www.rarbg.to/bot_check.php', method='post', data=post_data)
                    if re.search(r'You have been successfully verified as a human', page) is not None:
                        __addon__.log('Captcha solved successfully!')
                        page = load_page(*args, **kwargs)
                        break
                    else:
                        __addon__.log('Unable to solve the captcha!', LOGERROR)
                        page = load_page(*args, **kwargs)
                        continue
                else:
                    __addon__.log('Solving captcha is cancelled.')
                    page = ''
                    break
        return page
    return wrapper
