# This file is part of gtkPacman.

# gtkPacman is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# gtkPacman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with gtkPacman; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# gtkPacman is copyright (C)2005-2006 by Stefano Esposito

from time import sleep

from gtk import Dialog, MessageDialog, AboutDialog, FileChooserDialog
from gtk import Expander, ListStore, TreeView, HPaned, Frame, Label, Button
from gtk import Window, WINDOW_TOPLEVEL, WIN_POS_CENTER, VBox, Entry
from gtk import CellRendererPixbuf, CellRendererText
from gtk import STOCK_CLOSE, STOCK_OK, STOCK_CANCEL, STOCK_GO_FORWARD
from gtk import STOCK_APPLY, STOCK_REMOVE, STOCK_YES, STOCK_NO, STOCK_OPEN
from gtk import DIALOG_MODAL, DIALOG_DESTROY_WITH_PARENT
from gtk import MESSAGE_WARNING, FILE_CHOOSER_ACTION_OPEN
from gtk import BUTTONS_CLOSE
from gtk import RESPONSE_ACCEPT, RESPONSE_REJECT, RESPONSE_YES, RESPONSE_CLOSE
from gtk import image_new_from_stock, ICON_SIZE_BUTTON, ICON_SIZE_DIALOG
from gtk import main_iteration
from gtk.gdk import pixbuf_new_from_file

from terminal import terminal

class non_root_dialog(MessageDialog):

    def __init__(self, icon):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_WARNING, BUTTONS_CLOSE,
                               _("You must be root to fully use gtkpacman.\nSince you aren't root, gtkpacman will not allow any packages management operation (Install/Remove)"))
        self.set_icon (pixbuf_new_from_file(icon))

class confirm_dialog(Dialog):

    def __init__(self, parent, queues, icon):

        Dialog.__init__(self, _("Confirm"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_trees(queues)
        self._setup_layout()

    def _setup_trees(self, queues):

        self._setup_install_tree(queues["add"])
        self._setup_remove_tree (queues["remove"])

    def _setup_install_tree(self, queue):
        
        self.install_tree = TreeView()
        self.install_model = ListStore(str, str, str)

        self.install_tree.insert_column_with_attributes(-1, "",
                                                        CellRendererPixbuf(),
                                                        stock_id=0)
        self.install_tree.insert_column_with_attributes(-1, _("Package"),
                                                        CellRendererText(),
                                                        text=1)
        self.install_tree.insert_column_with_attributes(-1, _("Version"),
                                                        CellRendererText(),
                                                        text=2)

        for pac in queue:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.install_model.append([image, pac.name, pac.version])
            continue
        self.install_tree.set_model(self.install_model)
        return

    def _setup_remove_tree(self, queue):
        
        self.remove_tree = TreeView()
        self.remove_model = ListStore(str, str, str)

        self.remove_tree.insert_column_with_attributes(-1, "",
                                                       CellRendererPixbuf(),
                                                       stock_id=0)
        self.remove_tree.insert_column_with_attributes(-1, _("Package"),
                                                       CellRendererText(),
                                                       text=1)
        self.remove_tree.insert_column_with_attributes(-1, _("Version"),
                                                       CellRendererText(),
                                                       text=2)
        
        for pac in queue:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.remove_model.append([image, pac.name, pac.version])
            continue
        self.remove_tree.set_model(self.remove_model)
        return

    def _setup_layout(self):

        hpaned = HPaned()
        label = Label(_("Are you sure you want to install/remove those packages?"))
        label.show()
        inst_frame = Frame(_("Packages to install"))
        rem_frame = Frame(_("Packages to remove"))
        
        inst_frame.add(self.install_tree)
        rem_frame.add(self.remove_tree)

        hpaned.add1(inst_frame)
        hpaned.add2(rem_frame)
        
        hpaned.show_all()

        self.vbox.pack_start(label, False, False, 0)
        self.vbox.pack_start(hpaned, True, True, 0)
        return

    def run(self):
        response = Dialog.run(self)
        self.destroy()
        if response == RESPONSE_ACCEPT:
            return True
        else:
            return False

class warning_dialog(Dialog):

    def __init__(self, parent, pacs, icon):

        Dialog.__init__(self, _("Warning!"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_YES, RESPONSE_YES, STOCK_NO, RESPONSE_REJECT))

        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_tree(pacs)
        self._setup_layout()

    def _setup_layout(self):

        label = Label(_("This packages requires one of the packages you've selected for removal.\nDo you want to remove them all?"))
        label.show()

        self.vbox.pack_start(label, False, False, 0)
        self.vbox.pack_start(self.tree, True, True, 0)
        return

    def _setup_tree(self, pacs):
        self.tree = TreeView()
        self.model = ListStore(str, str, str)

        self.tree.insert_column_with_attributes(-1, "",
                                                CellRendererPixbuf(),
                                                stock_id=0)
        self.tree.insert_column_with_attributes(-1, "",
                                                CellRendererText(),
                                                text=1)
        self.tree.insert_column_with_attributes(-1, "",
                                                CellRendererText(),
                                                text=2)

        for pac in pacs:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.model.append([image, pac.name, pac.inst_ver])
            continue

        self.tree.set_model(self.model)
        self.tree.show_all()
        return

class about_dialog(AboutDialog):

    def __init__(self, icon):
        from os.path import exists, abspath, join
        from gtk.gdk import pixbuf_new_from_file
        AboutDialog.__init__(self)

        self.set_icon(pixbuf_new_from_file(icon))
        self.set_name("gtkpacman")
        self.set_version("svn")
        self.set_copyright(_("Copyright (C)2005-2006 by Stefano Esposito.\nRights to copy, modify, and redistribute are granted under the GNU General Public License Terms"))
        self.set_comments(_("Gtk package manager based on pacman"))
        self.set_license(_("""gtkPacman is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

gtkPacman program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA"""))
        self.set_website("http://gtkpacman.berlios.de")
        self.set_authors(["Stefano Esposito <ragnarok@email.it>"])
        self.set_artists(["James D <jamesgecko@gmail.com>"])

        path = "/usr/share/gtkpacman/"
        if not exists(path):
            path = abspath("data/")
            
        fname = join(path, "icons/pacman.png")
        logo = pixbuf_new_from_file(fname)
        self.set_logo(logo)

class do_dialog(Window):

    def __init__(self, queues):

        Window.__init__(self, WINDOW_TOPLEVEL)
        self.set_property("skip-taskbar-hint", True)
        self.set_property("destroy-with-parent", True)
        self.set_modal(True)
        self.connect("delete-event", self._stop_closing)
        self.set_position(WIN_POS_CENTER)

        self._setup_trees(queues)
        self._setup_layout()

        self.queues = queues

    def _setup_trees(self, queues):

        self._setup_install_tree(queues["add"])
        self._setup_remove_tree(queues["remove"])

    def _setup_install_tree(self, add_queue):

        self.inst_model = ListStore(str, str, str)

        for pac in add_queue:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.inst_model.append([image, pac.name, pac.version])
            continue

        self.inst_tree = TreeView()

        self.inst_tree.insert_column_with_attributes(-1, "",
                                                     CellRendererPixbuf(),
                                                     stock_id = 0)
        self.inst_tree.insert_column_with_attributes(-1, _("Package"),
                                                     CellRendererText(),
                                                     text = 1)
        self.inst_tree.insert_column_with_attributes(-1, _("Version"),
                                                     CellRendererText(),
                                                     text = 2)
        self.inst_tree.set_model(self.inst_model)

    def _setup_remove_tree(self, remove_queue):

        self.rem_model = ListStore(str, str, str)

        for pac in remove_queue:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.rem_model.append([image, pac.name, pac.inst_ver])
            continue

        self.rem_tree = TreeView()

        self.rem_tree.insert_column_with_attributes(-1, "",
                                                    CellRendererPixbuf(),
                                                    stock_id = 0)
        self.rem_tree.insert_column_with_attributes(-1, _("Package"),
                                                    CellRendererText(),
                                                    text = 1)
        self.rem_tree.insert_column_with_attributes(-1, _("Installed Version"),
                                                    CellRendererText(),
                                                    text = 2)

        self.rem_tree.set_model(self.rem_model)

    def _setup_layout(self):

        self.hpaned = HPaned()
        self.hpaned.add1(self.inst_tree)
        self.hpaned.add2(self.rem_tree)

        self.close_button = Button(stock=STOCK_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())

        self.terminal = terminal()
        self.terminal.connect("child-exited", lambda _: self.close_button.show())

        self.expander = Expander(_("Terminal"))
        self.expander.add(self.terminal)

        self.vbox = VBox(False, 0)
        self.vbox.pack_start(self.hpaned, False, False, 0)
        self.vbox.pack_start(self.expander, False, False, 0)
        self.vbox.pack_start(self.close_button, False, False, 0)

        self.vbox.show_all()
        self.close_button.hide()
        
        self.add(self.vbox)

    def run(self):

        self.show()
        self.terminal.do(self.queues)
        return

    def close(self, widget):
        self.destroy()

    def _stop_closing(self, widget, event):
        self.stop_emission("delete-event")
        return True

class local_install_fchooser_dialog(FileChooserDialog):

    def __init__(self, parent):
        FileChooserDialog.__init__(self, _("Choose package to install"),
                                   parent, FILE_CHOOSER_ACTION_OPEN,
                                   (STOCK_OPEN, RESPONSE_ACCEPT,
                                    STOCK_CANCEL, RESPONSE_REJECT))

class local_confirm_dialog(confirm_dialog):

    def __init__(self, parent, fname, pacs_queue):
        from os.path import basename
        
        confirm_dialog.__init__(self, parent, pacs_queue)
        package = basename(fname)

        name_n_ver = package.split("-", package.count("-")-1)
        version = name_n_ver.pop()
        name = "-".join(name_n_ver)

        self.install_model.prepend(["red", name, version])

class local_install_dialog(do_dialog):

    def __init__(self, fname, pacs_queue):
        from os.path import basename
        
        do_dialog.__init__(self, pacs_queue)

        package = basename(fname)
        
        name_n_ver = package.split("-", package.count("-")-1)
        version = name_n_ver.pop()
        name = "-".join(name_n_ver)

        self.inst_model.prepend(["red", name, version])
        self.fname = fname
        self.pacs_queue = pacs_queue

    def run(self):
        self.show()
        self.terminal.do_local(self.fname, self.pacs_queue)
        return
        
    
class search_dialog(Dialog):

    def __init__(self, parent):

        Dialog.__init__(self, _("Search for.."), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

        self._setup_layout()

    def _setup_layout(self):

        self.label = Label(_("Insert keywords:"))

        self.entry = Entry()
        self.entry.connect("activate", self._entry_response)

        self.vbox.pack_start(self.label, False, False, 0)
        self.vbox.pack_start(self.entry, False, False, 0)

        self.vbox.show_all()

    def _entry_response(self, widget, data=None):
        self.response(RESPONSE_ACCEPT)

class upgrade_dialog(Window):

    def __init__(self, to_upgrade):

        Window.__init__(self, WINDOW_TOPLEVEL)
        self.set_property("skip-taskbar-hint", True)
        self.set_property("modal", True)
        self.set_property("destroy-with-parent", True)
        self.set_position(WIN_POS_CENTER)

        self._setup_tree(to_upgrade)
        self._setup_layout()

    def _setup_layout(self):
        self.vbox = VBox(False, 0)

        self.terminal = terminal()
        self.terminal.connect("child-exited", lambda _: self.close_button.show())
        self.close_button = Button(stock=STOCK_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())

        self.vbox.pack_start(self.tree, False, False, 0)
        self.vbox.pack_start(self.terminal, False, False, 0)
        self.vbox.pack_start(self.close_button, False, False, 0)

        self.tree.show()
        self.terminal.show()
        self.vbox.show()
        return

    def _setup_tree(self, pacs):
        self.model = ListStore(str, str, str)

        for pac in pacs:
            self.model.append("yellow", pac.name, pac.version)
            continue

        self.tree = TreeView()

        self.tree.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                                stock_id = 0)
        self.tree.insert_column_with_attributes(-1, "Package",
                                                CellRendererText(), text = 1)
        self.tree.insert_column_with_attributes(-1, "Version",
                                                CellRendererText(), text = 2)

        self.tree.set_model(self.model)
        return
    
    def run(self):
        self.show()
        self.terminal.do_upgrade()

class upgrade_confirm_dialog(Dialog):

    def __init__(self, parent, to_upgrade):

        Dialog.__init__(self, _("Confirm Upgrade"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

        self._setup_tree(to_upgrade)
        self._setup_layout()

    def _setup_tree(self, pacs):
        self.model = ListStore(str, str, str)

        for pac in pacs:
            self.model.append(["yellow", pac.name, pac.version])
            continue

        self.tree = TreeView()
        self.tree.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                                stock_id = 0)
        self.tree.insert_column_with_attributes(-1, "Package",
                                                CellRendererText(), text = 1)
        self.tree.insert_column_with_attributes(-1, "Version",
                                                CellRendererText(), text = 2)

        self.tree.set_model(self.model)
        self.tree.show()

    def _setup_layout(self):

        self.label = Label(_("Are you sure yo want to upgrade those packages?\n"))
        self.label.show()
        
        self.vbox.pack_start(self.label, False, False, 0)
        self.vbox.pack_start(self.tree, False, False, 0)

    def run(self):
        retcode = Dialog.run(self)
        self.destroy()

        if retcode == RESPONSE_ACCEPT:
            return True
        else:
            return False

class refresh_dialog(Window):

    def __init__(self):

        Window.__init__(self, WINDOW_TOPLEVEL)
        self.set_property("skip-taskbar-hint", True)
        self.set_property("destroy-with-parent", True)
        self.set_modal(True)
        self.set_position(WIN_POS_CENTER)

        self.vbox = VBox(False, 0)
        
        self.terminal = terminal()
        self.terminal.connect("child-exited",
                              lambda _: self.close_button.show())
        
        self.close_button = Button(stock=STOCK_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())

        self.vbox.pack_start(self.terminal, False, False, 0)
        self.vbox.pack_start(self.close_button, False, False, 0)

        self.add(self.vbox)

        self.terminal.show()
        self.vbox.show()

    def run(self):

        self.show()
        self.terminal.fork_command()
        self.terminal.feed_child("pacman -Sy;exit\n")
        
    def _close(self, terminal, data=None):
        self.close_button.show()
        return
        
        
