# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

import re
import xbmcgui
import pyxbmct
from simpleplugin import Plugin
from tvdb import get_series, TvdbError

dialog = xbmcgui.Dialog()
plugin = Plugin()


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
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200'),
                               ('WindowClose', 'effect=fade start=100 end=0 time=200')])

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
            self.filter = {}
        else:
            title = 'Edit Filter'
            self.filter = filter_
        super(FilterEditor, self).__init__()
        self.setWindowTitle(title)
        self.dirty = False
        self.delete = False

    def _set_controls(self):
        name_label = pyxbmct.Label('Name:')
        self.placeControl(name_label, 0, 0)
        self._filter_name = pyxbmct.Label(self.filter.get('name', ''))
        self.placeControl(self._filter_name, 0, 1, columnspan=2)
        tvdb_label = pyxbmct.Label('[B]TheTVDB ID[/B]:')
        self.placeControl(tvdb_label, 1, 0)
        self._tvdb_edit = pyxbmct.Edit('')
        self.placeControl(self._tvdb_edit, 1, 1, columnspan=2)
        self._tvdb_edit.setText(self.filter.get('tvdb', ''))
        extra_label = pyxbmct.Label('Additional filter:')
        self.placeControl(extra_label, 2, 0)
        self._extra_edit = pyxbmct.Edit('')
        self.placeControl(self._extra_edit, 2, 1, columnspan=2)
        self._extra_edit.setText(self.filter.get('extra_filter', ''))
        exclude_label = pyxbmct.Label('Exclude:')
        self.placeControl(exclude_label, 3, 0)
        self._exclude_edit = pyxbmct.Edit('')
        self.placeControl(self._exclude_edit, 3, 1, columnspan=2)
        self._exclude_edit.setText(self.filter.get('exclude', ''))
        save_path_label = pyxbmct.Label('[B]Download folder[/B]:')
        self.placeControl(save_path_label, 4, 0)
        self._select_folder_button = pyxbmct.Button(self.filter.get('save_path', ''), alignment=pyxbmct.ALIGN_LEFT)
        self.placeControl(self._select_folder_button, 4, 1, columnspan=2)
        self._delete_button = pyxbmct.Button('Delete filter')
        self.placeControl(self._delete_button, 5, 0)
        if not self.filter.get('tvdb'):
            self._delete_button.setVisible(False)
        self._cancel_button = pyxbmct.Button('Cancel')
        self.placeControl(self._cancel_button, 5, 1)
        self._save_button = pyxbmct.Button('Save filter')
        self.placeControl(self._save_button, 5, 2)

    def _set_connections(self):
        super(FilterEditor, self)._set_connections()
        self.connect(self._select_folder_button, self._select_save_path)
        self.connect(self._delete_button, self._delete)
        self.connect(self._cancel_button, self.close)
        self.connect(self._save_button, self._save)

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

    def _select_save_path(self):
        self._select_folder_button.setLabel(dialog.browseSingle(0, 'Select download folder', 'video',
                                                                defaultt=self.filter.get('save_path', '')))

    def _validate(self):
        if not (self._tvdb_edit.getText() and self._select_folder_button.getLabel()):
            dialog.ok('Invalid input!', '"TheTVDB ID" and "Download folder" fields must not be empty.')
            return False
        elif not re.search(r'^\d+$', self._tvdb_edit.getText()):
            dialog.ok('Invalid TheTVDB ID!', '"TheTVDB ID" field must contain only numbers.')
            return False
        else:
            with plugin.get_storage('tvshows.pcl') as tvshows:
                show = tvshows.get(self.filter['tvdb'])
                if show is None:
                    try:
                        show = get_series(self.filter['tvdb'])
                    except TvdbError:
                        dialog.ok('Invalid TheTVDB ID!', 'TheTVDB does not have a TV show with such ID.')
                        return False
                    else:
                        tvshows[self.filter['tvdb']] = show
                self.filter['name'] = show['SeriesName']
                self._filter_name.setLabel(show['SeriesName'])
                return True

    def _save(self):
        if self._validate():
            self.filter['tvdb'] = self._tvdb_edit.getText()
            self.filter['extra_filter'] = self._extra_edit.getText()
            self.filter['exclude'] = self._exclude_edit.getText()
            self.filter['save_path'] = self._select_folder_button.getLabel()
            self.dirty = True
            self.close()

    def _delete(self):
        self.delete = True
        self.close()


class FilterList(RarbgDialog):
    """
    Shows the list of episode download filters
    """
    def __init__(self, filters=None):
        super(FilterList, self).__init__()
        self.setWindowTitle('Autodownload Filters')
        self.dirty = False
        self._filters = filters
        self._populate_list()

    def _set_controls(self):
        self._filter_list = pyxbmct.List()
        self.placeControl(self._filter_list, 0, 0, rowspan=5, columnspan=3)
        self._new_button = pyxbmct.Button('New filter...')
        self.placeControl(self._new_button, 5, 0)
        self._cancel_button = pyxbmct.Button('Cancel')
        self.placeControl(self._cancel_button, 5, 1)
        self._save_button = pyxbmct.Button('Save filters')
        self.placeControl(self._save_button, 5, 2)

    def _set_connections(self):
        super(FilterList, self)._set_connections()
        self.connect(self._filter_list, self._open_editor)
        self.connect(self._save_button, self.close)
        self.connect(self._cancel_button, self._cancel)
        self.connect(self._new_button, self._open_editor)

    def _set_navigation(self):
        self._filter_list.controlUp(self._save_button)
        self._filter_list.controlDown(self._save_button)
        self._new_button.setNavigation(self._filter_list, self._filter_list, self._save_button, self._cancel_button)
        self._cancel_button.setNavigation(self._filter_list, self._filter_list, self._new_button, self._save_button)
        self._save_button.setNavigation(self._filter_list, self._filter_list, self._cancel_button, self._new_button)
        self.setFocus(self._cancel_button)

    @property
    def filters(self):
        return self._filters

    def _populate_list(self):
        self._filter_list.reset()
        for key, value in self._filters.iteritems():
            self._filter_list.addItem(xbmcgui.ListItem(label=value['name'], label2=key))
        if self._filter_list.size():
            self.setFocus(self._filter_list)
        else:
            self.setFocus(self._cancel_button)

    def _open_editor(self):
        if self.getFocus() == self._filter_list:
            tvdb = self._filter_list. getListItem(self._filter_list.getSelectedPosition()).getLabel2()
            filter_ = self._filters[tvdb]
            filter_['tvdb'] = tvdb
        else:
            filter_ = None
        editor = FilterEditor(filter_)
        self.close()
        editor.doModal()
        if editor.delete or editor.dirty:
            if editor.delete:
                del self._filters[editor.filter['tvdb']]
            elif editor.dirty:
                self._filters[editor.filter['tvdb']] = editor.filter
            self.dirty = True
            self._populate_list()
        del editor
        self.doModal()

    def _cancel(self):
        if self.dirty and dialog.yesno('Unsaved changes!', 'Dou you want to leave without saving filters?'):
            self.dirty = False
        if not self.dirty:
            self.close()

