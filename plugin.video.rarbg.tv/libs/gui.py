# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

import xbmcgui
import pyxbmct


class RarbgDialog(pyxbmct.AddonDialogWindow):
    """
    Abstract base class for dialogs
    """
    def __init__(self):
        super(RarbgDialog, self).__init__()
        self.setGeometry(300, 600, 6, 3)
        self._set_controls()
        self._set_connections()
        self._set_navigation()

    def _set_controls(self):
        raise NotImplementedError

    def _set_connections(self):
        self.connect(xbmcgui.ACTION_NAV_BACK, self.close)

    def _set_navigation(self):
        raise NotImplementedError
