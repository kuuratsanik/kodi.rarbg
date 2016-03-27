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
        self.setGeometry(550, 300, 6, 3)
        self._set_controls()
        self._set_connections()
        self._set_navigation()

    def setAnimation(self, control):
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=250'),
                               ('WindowClose', 'effect=fade start=100 end=0 time=250')])

    def _set_controls(self):
        raise NotImplementedError

    def _set_connections(self):
        self.connect(xbmcgui.ACTION_NAV_BACK, self.close)

    def _set_navigation(self):
        raise NotImplementedError


class FilterEditor(RarbgDialog):
    """
    Add or edit a download filter
    """
    def __init__(self, filter_=None):
        if filter_ is None:
            title = 'New Filter'
            self.filter = {'name': '', 'tvdb': '', 'extra_filter': '', 'exclude': '', 'save_path': ''}
        else:
            title = 'Edit Filter'
            self.filter = filter_
        super(FilterEditor, self).__init__()
        self.setWindowTitle(title)

    def _set_controls(self):
        name_label = pyxbmct.Label('Name:')
        self.placeControl(name_label, 0, 0)
        filter_name = pyxbmct.Label(self.filter['name'])
        self.placeControl(filter_name, 0, 1, columnspan=2)
        tvdb_label = pyxbmct.Label('[B]TheTVDB ID[/B]:')
        self.placeControl(tvdb_label, 1, 0)
        self._tvdb_edit = pyxbmct.Edit('')
        self.placeControl(self._tvdb_edit, 1, 1, columnspan=2)
        self._tvdb_edit.setText(self.filter['tvdb'])
        extra_label = pyxbmct.Label('Additional filter:')
        self.placeControl(extra_label, 2, 0)
        self._extra_edit = pyxbmct.Edit('')
        self.placeControl(self._extra_edit, 2, 1, columnspan=2)
        self._extra_edit.setText(self.filter['extra_filter'])
        exclude_label = pyxbmct.Label('Exclude:')
        self.placeControl(exclude_label, 3, 0)
        self._exclude_edit = pyxbmct.Edit('')
        self.placeControl(self._exclude_edit, 3, 1, columnspan=2)
        self._exclude_edit.setText(self.filter['exclude'])
        save_path_label = pyxbmct.Label('[B]Download folder[/B]:')
        self.placeControl(save_path_label, 4, 0)
        self._select_folder_button = pyxbmct.Button(self.filter['save_path'], alignment=pyxbmct.ALIGN_LEFT)
        self.placeControl(self._select_folder_button, 4, 1, columnspan=2)
        self._delete_button = pyxbmct.Button('Delete filter')
        self.placeControl(self._delete_button, 5, 0)
        if not self.filter['tvdb']:
            self._delete_button.setVisible(False)
        self._cancel_button = pyxbmct.Button('Cancel')
        self.placeControl(self._cancel_button, 5, 1)
        self._save_button = pyxbmct.Button('Save filter')
        self.placeControl(self._save_button, 5, 2)

    def _set_connections(self):
        super(FilterEditor, self)._set_connections()

    def _set_navigation(self):
        self._tvdb_edit.controlUp(self._save_button)
        self._tvdb_edit.controlDown(self._extra_edit)
        self._extra_edit.controlUp(self._tvdb_edit)
        self._extra_edit.controlDown(self._exclude_edit)
        self._exclude_edit.controlUp(self._extra_edit)
        self._exclude_edit.controlDown(self._select_folder_button)
        self._select_folder_button.controlUp(self._exclude_edit)
        self._select_folder_button.controlDown(self._save_button)
        self._delete_button.setNavigation(self._select_folder_button, self._tvdb_edit,
                                          self._save_button, self._cancel_button)
        self._cancel_button.setNavigation(self._select_folder_button, self._tvdb_edit,
                                          self._delete_button, self._save_button)
        self._save_button.setNavigation(self._select_folder_button, self._tvdb_edit,
                                        self._cancel_button, self._delete_button)
        self.setFocus(self._tvdb_edit)


class FilterList(RarbgDialog):
    """
    Shows the list of episode download filters
    """
    def __init__(self, filters=None):
        super(FilterList, self).__init__()
        self.setWindowTitle('Autodownloading Filters')
        self._dirty = False
        self._filters = filters

    def _set_controls(self):
        self._list_control = pyxbmct.List()
        self.placeControl(self._list_control, 0, 0, rowspan=5, columnspan=3)
        self._new_button = pyxbmct.Button('New filter...')
        self.placeControl(self._new_button, 5, 0)
        self._cancel_button = pyxbmct.Button('Cancel')
        self.placeControl(self._cancel_button, 5, 1)
        self._save_button = pyxbmct.Button('Save filters')
        self.placeControl(self._save_button, 5, 2)

    def _set_connections(self):
        super(FilterList, self)._set_connections()

    def _set_navigation(self):
        self._list_control.controlUp(self._save_button)
        self._list_control.controlDown(self._save_button)
        self._new_button.setNavigation(self._list_control, self._list_control, self._save_button, self._cancel_button)
        self._cancel_button.setNavigation(self._list_control, self._list_control, self._new_button, self._save_button)
        self._save_button.setNavigation(self._list_control, self._list_control, self._cancel_button, self._new_button)

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, value):
        self._filters = value
        self._list_control.addItems([item['name'] for item in value.itervalues()])
        self._dirty = False
