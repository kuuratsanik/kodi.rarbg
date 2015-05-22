# -*- coding: utf-8 -*-
# Module: anticaptcha
# Author: Roman V.M.
# Created on: 20.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import pyxbmct.addonwindow as pyxbmct


class Dialog(pyxbmct.AddonDialogWindow):
    """
    Dialog for solving captcha check
    """
    def __init__(self, captcha=''):
        super(Dialog, self).__init__()
        self.setGeometry(400, 250, 4, 2)
        self.setWindowTitle('Rarbg bot check!')
        self._confirmed = False
        self._set_controls(captcha)
        self._set_navigation()

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
        self.setFocus(self._edit)

    def _ok(self):
        self._confirmed = True
        super(Dialog, self).close()

    def close(self):
        self._confirmed = False
        super(Dialog, self).close()

    def set_captcha(self, image):
        self._image.setImage(image)

    @property
    def confirmed(self):
        return self._confirmed

    @property
    def text(self):
        return self._edit.getText()
