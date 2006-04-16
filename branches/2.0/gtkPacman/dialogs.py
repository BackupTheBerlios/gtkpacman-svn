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

from gtk import Dialog, MessageDialog, AboutDialog
from gtk import Expander, ListStore, TreeView, HPaned, Frame, Label, Button
from gtk import Window, WINDOW_TOPLEVEL, VBox
from gtk import CellRendererPixbuf, CellRendererText
from gtk import STOCK_CLOSE, STOCK_OK, STOCK_CANCEL, STOCK_GO_FORWARD
from gtk import STOCK_APPLY, STOCK_REMOVE
from gtk import DIALOG_MODAL, DIALOG_DESTROY_WITH_PARENT
from gtk import MESSAGE_ERROR
from gtk import BUTTONS_CLOSE
from gtk import RESPONSE_ACCEPT, RESPONSE_REJECT, RESPONSE_YES, RESPONSE_CLOSE
from gtk import image_new_from_stock, ICON_SIZE_BUTTON, ICON_SIZE_DIALOG
from gtk import main_iteration

from terminal import terminal

class non_root_dialog(MessageDialog):

    def __init__(self):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_ERROR, BUTTONS_CLOSE,
                               _("You have to be root to run gtkpacman!"))

class confirm_dialog(Dialog):

    def __init__(self, parent, queues):

        Dialog.__init__(self, _("Confirm"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

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

    def __init__(self, parent, pacs):

        Dialog.__init__(self, _("Warning!"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT)

        self._setup_buttons()
        self._setup_tree(pacs)
        self._setup_layout()

    def _setup_buttons(self):
        rem_all_img = image_new_from_stock(STOCK_REMOVE, ICON_SIZE_BUTTON)
        rem_all_butt = Button(_("Remove All"))
        rem_all_butt.set_image(rem_all_img)
        rem_all_butt.show()

        rem_img = image_new_from_stock(STOCK_CANCEL, ICON_SIZE_BUTTON)
        rem_butt = Button(_("Force"))
        rem_butt.set_image(rem_img)
        rem_butt.show()

        close_butt = Button(stock=STOCK_CLOSE)
        close_butt.show()

        self.add_action_widget(rem_all_butt, RESPONSE_ACCEPT)
        self.add_action_widget(rem_butt, RESPONSE_YES)
        self.add_action_widget(close_butt, RESPONSE_CLOSE)

    def _setup_layout(self):

        label = Label(_("This packages requires one of the packages you've selected for removal.\nDo you want to remove them all,, or do you want to force the removal\nof the selected packages only?(This will probably break dependent packages)"))
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

    def run(self):
        response = Dialog.run(self)

        if response == RESPONSE_ACCEPT:
            return 1
        elif response == RESPONSE_YES:
            return 2
        else:
            return 0

class about_dialog(AboutDialog):

    def __init__(self):
        from os.path import exists, abspath, join
        from gtk.gdk import pixbuf_new_from_file
        AboutDialog.__init__(self)

        self.set_name("gtkpacman")
        self.set_version("2.0-alpha1")
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

        self._setup_trees(queues)
        self._setup_layout()

        self.connect("delete-event", self._stop_closing)
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
        self.close_button.connect("clicked", self.close)

        self.expander = Expander(_("Terminal"))
        self.terminal = terminal(self.close_button)
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
    
