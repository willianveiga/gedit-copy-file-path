# Copy File Path Plugin - Copy current file path to the clipboard.
# Copyright (C) <2015>  <Willian Gustavo Veiga>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gettext import gettext as _
from gi.repository import GObject, Gtk, Gdk, Gio, Gedit


class CopyFilePathPlugin:
    def copy_file_path(self, document):
        self.copy_to_clipboard(document.get_uri_for_display())

    def copy_to_clipboard(self, file_path):
        clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        Gtk.Clipboard.set_text(clipboard, file_path, len(file_path))
        clipboard.store()

    def document_loaded(self, document):
        return document is not None and document.get_location() is not None


class CopyFilePathPluginAppActivatable(GObject.Object, Gedit.AppActivatable):

    __gtype_name__ = 'CopyFilePathPluginAppActivatable'

    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.insert_menu()

    def do_deactivate(self):
        self.menu_ext = None

    def insert_menu(self):
        self.menu_ext = self.extend_menu('tools-section')
        item = Gio.MenuItem.new(_('Copy file path to the clipboard'),
                                'win.copyfilepath')
        self.menu_ext.prepend_menu_item(item)


class CopyFilePathPluginWindowActivatable(GObject.Object,
                                          Gedit.WindowActivatable):

    __gtype_name__ = 'CopyFilePathPluginWindowActivatable'

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.copy_file_path_plugin = CopyFilePathPlugin()

        action = Gio.SimpleAction(name='copyfilepath')
        action.connect('activate', lambda i, j: self.do_copy_file_path())
        self.window.add_action(action)

        self.do_update_state()

    def do_update_state(self):
        document = self.window.get_active_document()
        enable = self.copy_file_path_plugin.document_loaded(document)
        self.window.lookup_action('copyfilepath').set_enabled(enable)

    def do_deactivate(self):
        self.copy_file_path_plugin = None

    def do_copy_file_path(self):
        document = self.window.get_active_document()
        self.copy_file_path_plugin.copy_file_path(document)


class CopyFilePathPluginViewActivatable(GObject.Object, Gedit.ViewActivatable):

    __gtype_name__ = 'CopyFilePathPluginViewActivatable'

    view = GObject.Property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.copy_file_path_plugin = CopyFilePathPlugin()
        self.populate_popup_handler_id = self.view.connect('populate-popup',
                                                           self.populate_popup)

    def do_deactivate(self):
        self.view.disconnect(self.populate_popup_handler_id)

        self.copy_file_path_plugin = None
        self.populate_popup_handler_id = None

    def populate_popup(self, view, popup):
        item = Gtk.SeparatorMenuItem()
        item.show()
        popup.append(item)

        label = _('Copy file path to the clipboard')
        item = Gtk.MenuItem.new_with_label(label)

        document = self.view.get_buffer()
        sensitive = self.copy_file_path_plugin.document_loaded(document)
        item.set_sensitive(sensitive)

        item.show()
        item.connect('activate', lambda i: self.do_copy_file_path())
        popup.append(item)

    def do_copy_file_path(self):
        self.copy_file_path_plugin.copy_file_path(self.view.get_buffer())

