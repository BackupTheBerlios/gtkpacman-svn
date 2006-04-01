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

from gtk import Dialog, MessageDialog, AboutDialog
from gtk import Expander, ListStore, TreeView, HPaned, Frame, Label
from gtk import CellRendererPixbuf, CellRendererText
from gtk import STOCK_CLOSE, STOCK_OK, STOCK_CANCEL, STOCK_GO_FORWARD
from gtk import STOCK_APPLY
from gtk import DIALOG_MODAL, DIALOG_DESTROY_WITH_PARENT
from gtk import MESSAGE_ERROR
from gtk import BUTTONS_CLOSE
from gtk import RESPONSE_ACCEPT, RESPONSE_REJECT
from gtk import image_new_from_stock, ICON_SIZE_BUTTON, ICON_SIZE_DIALOG

from terminal import terminal

class non_root_dialog(MessageDialog):

    def __init__(self):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_ERROR, BUTTONS_CLOSE,
                               "You have to be root to run gtkpacman!")

class confirm_dialog(Dialog):

    def __init__(self, parent, queues):

        Dialog.__init__(self, "Confirm", parent,
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
        self.install_tree.insert_column_with_attributes(-1, "Package",
                                                        CellRendererText(),
                                                        text=1)
        self.install_tree.insert_column_with_attributes(-1, "Version",
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
        self.remove_tree.insert_column_with_attributes(-1, "Package",
                                                       CellRendererText(),
                                                       text=1)
        self.remove_tree.insert_column_with_attributes(-1, "Version",
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
        label = Label("Are you sure you want to install/remove those packages?")
        label.show()
        inst_frame = Frame("Packages to install")
        rem_frame = Frame("Packages to remove")
        
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

class do_dialog(Dialog):

    def __init__(self, parent, queues):

        Dialog.__init__(self, "Operations in progress...", parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT)

        self._setup_trees(queues)
        self._setup_layout()

        self.queues = queues

    def _setup_trees(self, queues):

        self._setup_install_tree(queues["add"])
        self._setup_remove_tree (queues["remove"])

    def _setup_install_tree(self, queue):
        
        self.install_tree = TreeView()
        self.install_model = ListStore(str, str, str, str)

        self.install_tree.insert_column_with_attributes(-1, "",
                                                        CellRendererPixbuf(),
                                                        stock_id=0)
        self.install_tree.insert_column_with_attributes(-1, "",
                                                        CellRendererPixbuf(),
                                                        stock_id=1)
        self.install_tree.insert_column_with_attributes(-1, "Package",
                                                        CellRendererText(),
                                                        text=2)
        self.install_tree.insert_column_with_attributes(-1, "Version",
                                                        CellRendererText(),
                                                        text=3)

        for pac in queue:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.install_model.append([None, image, pac.name, pac.version])
            continue
        self.install_tree.set_model(self.install_model)
        return

    def _setup_remove_tree(self, queue):
        
        self.remove_tree = TreeView()
        self.remove_model = ListStore(str, str, str, str)

        self.remove_tree.insert_column_with_attributes(-1, "",
                                                       CellRendererPixbuf(),
                                                       stock_id=0)
        self.remove_tree.insert_column_with_attributes(-1, "",
                                                       CellRendererPixbuf(),
                                                       stock_id=1)
        self.remove_tree.insert_column_with_attributes(-1, "Package",
                                                       CellRendererText(),
                                                       text=2)
        self.remove_tree.insert_column_with_attributes(-1, "Version",
                                                       CellRendererText(),
                                                       text=3)
        
        for pac in queue:
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"

            self.remove_model.append([None, image, pac.name, pac.version])
            continue
        self.remove_tree.set_model(self.remove_model)
        return
                        
    def _setup_layout(self):

        hpaned = HPaned ()
        inst_frame = Frame("Packages being installed")
        rem_frame = Frame("Packages being removed")

        inst_frame.add(self.install_tree)
        rem_frame.add(self.remove_tree)

        hpaned.add1(inst_frame)
        hpaned.add2(rem_frame)

        hpaned.show_all()

        expander = Expander("Terminal")

        self.terminal = terminal(self.error, self.success)

        expander.add(self.terminal)
        expander.show_all()

        self.vbox.pack_start(hpaned, True, True, 0)
        self.vbox.pack_start(expander, True, True, 0)
        return

    def run(self, force):
        from thread import start_new_thread
        
        Dialog.run(self)

        self.errors = { "install": [], "remove": [] }
        for pac in self.queues["add"]:
            for row in self.install_model:
                if row[2] == pac.name:
                    row[0] == STOCK_GO_FORWARD
                    start_new_thread(self.terminal.install, (pac, row))
                continue
            continue

        for pac in self.queues["remove"]:
            for row in self.remove_model:
                if row[2] == pac.name:
                    row[0] == STOCK_GO_FORWARD
                    start_new_thread(self.terminal.remove, (pac, row, force))
                continue
            continue
        self.response(RESPONSE_ACCEPT)
        return

    def error(self, row, pac, what):

        row[0] = STOCK_CANCEL
        self.errors[what].append(pac)
        return

    def success (self, row):
        row[0] = STOCK_APPLY
        return

class warning_dialog(Dialog):

    def __init__(self, parent, pacs):

        Dialog.__init__(self, "Warning!", parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT)

        self._setup_buttons()
        self._setup_trees(pacs)
        self._setup_layout()

    def _setup_buttons(self):
        rem_all_img = image_new_from_stok(STOCK_REMOVE, ICON_SIZE_BUTTON)
        rem_all_butt = Button("Remove All")
        rem_all_butt.set_image(rem_all_img)
        rem_all_butt.show()

        rem_img = image_new_from_stock(STOCK_CANCEL, ICON_SIZE_BUTTON)
        rem_butt = Button("Force")
        rem_butt.set_image(rem_img)
        rem_butt.show()

        close_butt = Button(STOCK_CLOSE)
        close_butt.show()

        self.add_action_widget(rem_all_butt, RESPONSE_ACCEPT)
        self.add_action_widget(rem_butt, RESPONSE_YES)
        self.add_action_widget(close_butt, RESPONSE_CLOSE)

    def _setup_layout(self):

        label = Label("This packages requires one of the packages you've selected for removal.\nDo you want to remove them all,, or do you want to force the removal of the selected packages only?(This will probably break dependent packages")

        self.vbox.pack_start(label, False, False, 0)
        self.vbox.pack_start(self.tree, True, True, 0)
        return

    def _setup_tree(self, pacs):
        self.tree = Treeview()
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
        self.set_copyright("Copyright (C)2005-2006 by Stefano Esposito.\nRights to copy, modify, and redistribute are granted under the GNU General Publi License Terms")
        self.set_comments("Gtk package manager based on pacman")
        self.set_license("""gtkPacman is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

gtkPacman program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA""")
        self.set_website("http://gtkpacman.berlios.de")
        self.set_authors(["Stefano Esposito <ragnarok@email.it>"])
        self.set_artists(["James D <jamesgecko@gmail.com>"])

        path = "/usr/share/gtkpacman/"
        if not exists(path):
            path = abspath("data/")
            
        fname = join(path, "icons/pacman.png")
        logo = pixbuf_new_from_file(fname)
        self.set_logo(logo)
