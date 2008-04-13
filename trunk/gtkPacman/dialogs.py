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
# gtkPacman is copyright (C)2005-2008 by Stefano Esposito

from time import sleep

from gtk import Dialog, MessageDialog, AboutDialog, FileChooserDialog
from gtk import Expander, ListStore, TreeView, HPaned, Frame, Label, Button
from gtk import Window, WINDOW_TOPLEVEL, WIN_POS_CENTER, VBox, Entry
from gtk import ScrolledWindow, VPaned, POLICY_AUTOMATIC
from gtk import CellRendererPixbuf, CellRendererText
from gtk import STOCK_CLOSE, STOCK_OK, STOCK_CANCEL, STOCK_GO_FORWARD
from gtk import STOCK_APPLY, STOCK_REMOVE, STOCK_YES, STOCK_NO, STOCK_OPEN
from gtk import DIALOG_MODAL, DIALOG_DESTROY_WITH_PARENT, BUTTONS_OK_CANCEL
from gtk import MESSAGE_WARNING, FILE_CHOOSER_ACTION_OPEN, MESSAGE_INFO
from gtk import BUTTONS_CLOSE, BUTTONS_YES_NO, MESSAGE_ERROR, MESSAGE_QUESTION
from gtk import RESPONSE_ACCEPT, RESPONSE_REJECT, RESPONSE_YES, RESPONSE_CLOSE
from gtk import RESPONSE_NO, image_new_from_stock, ICON_SIZE_BUTTON
from gtk import ICON_SIZE_DIALOG, main_iteration, expander_new_with_mnemonic
from gtk import WIN_POS_CENTER_ON_PARENT
from gtk.gdk import pixbuf_new_from_file

from models import PacView
from terminal import terminal

class non_root_dialog(MessageDialog):

    def __init__(self, icon):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_WARNING, BUTTONS_CLOSE,
                               _("You must be root to fully use gtkpacman.\nSince you aren't root, gtkpacman will not allow any packages management operation (Install/Remove)"))
        self.set_icon (pixbuf_new_from_file(icon))

class ignorepkg_dialog(MessageDialog):

    def __init__(self, name, icon):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_QUESTION, BUTTONS_YES_NO,
                               _("Package %s is in IgnorePkg. Install it anyway?" %name))
        self.set_icon (pixbuf_new_from_file(icon))

class holdpkg_dialog(MessageDialog):

    def __init__(self, name, icon):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_INFO, BUTTONS_YES_NO,
                               _("Package %s is in HoldPkg. Are You sure you want to remove %s") %(name,name))
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

        self.install_tree = PacView(queues["add"])
        self.remove_tree = PacView(queues["remove"])

    def _setup_layout(self):

        hpaned = HPaned()
        label = Label(_("Are you sure you want to install/remove those packages?"))
        label.show()
        inst_frame = Frame(_("Packages to install"))
        rem_frame = Frame(_("Packages to remove"))

        inst_scroll = ScrolledWindow()
        inst_scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)

        rem_scroll = ScrolledWindow()
        rem_scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)

        inst_scroll.add(self.install_tree)
        rem_scroll.add(self.remove_tree)
        
        inst_frame.add(inst_scroll)
        rem_frame.add(rem_scroll)

        hpaned.pack1(inst_frame, False, False)
        hpaned.pack2(rem_frame, False, False)
        
        hpaned.show_all()

        self.vbox.pack_start(label, False, False, 0)
        self.vbox.pack_start(hpaned, True, True, 0)
        self.set_default_size(600,300)
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

        self.set_default_size(-1,250)
        
        label = Label(_("This packages requires one of the packages you've selected for removal.\nDo you want to remove them all?"))
        label.show()

        scr = ScrolledWindow()
        scr.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        scr.add(self.tree)

        self.vbox.pack_start(label, False, False, 0)
        self.vbox.pack_start(scr, True, True, 0)
        self.vbox.show_all()
        return

    def _setup_tree(self, pacs):

        self.tree = PacView(pacs)
        self.tree.show_all()
        return

class about_dialog(AboutDialog):

    def __init__(self, icon):
        from os.path import exists, abspath, join
        from gtk.gdk import pixbuf_new_from_file
        AboutDialog.__init__(self)

        self.set_icon(pixbuf_new_from_file(icon))
        self.set_name("gtkpacman")
        self.set_version("2.4dev")
        self.set_copyright(_("Copyright (C)2005-2008 by Stefano Esposito.\nRights to copy, modify, and redistribute are granted under the GNU General Public License Terms"))
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
        self.set_authors(["Stefano Esposito <stefano.esposito87@gmail.com>", "'Seti' <seti4ever@gmail.com"])
        self.set_artists(["James D <jamesgecko@gmail.com>"])

        path = "/usr/share/gtkpacman/"
        if not exists(path):
            path = abspath("data/")
            
        fname = join(path, "icons/pacman.png")
        logo = pixbuf_new_from_file(fname)
        self.set_logo(logo)

class do_dialog(Window):

    def __init__(self, parent, queues, icon):

        Window.__init__(self, WINDOW_TOPLEVEL)
        self.set_property("skip-taskbar-hint", True)
        self.set_property("destroy-with-parent", True)
        self.set_modal(True)
        self.set_transient_for(parent)
        self.connect("delete-event", self._stop_closing)
        self.set_position(WIN_POS_CENTER_ON_PARENT)

        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_trees(queues)
        self._setup_layout()

        self.queues = queues

    def _setup_trees(self, queues):

        self.install_tree = PacView(queues["add"])
        self.remove_tree = PacView(queues["remove"])

    def _set_size (self, widget, event, data=None):
        if self.expander.get_expanded():
            self.size = self.get_size()
            self.expander.add(self.terminal)
            self.terminal.show()
        else:
            self.expander.remove(self.terminal)
            self.resize(self.size[0], self.size[1])
            self.show_all()

    def _setup_layout(self):

        self.set_default_size(600,200)
        self.hpaned = HPaned()
        
        inst_scroll = ScrolledWindow()
        inst_scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)

        rem_scroll = ScrolledWindow()
        rem_scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        
        inst_scroll.add(self.install_tree)
        rem_scroll.add(self.remove_tree)
        
        self.hpaned.pack1(inst_scroll, False, False)
        self.hpaned.pack2(rem_scroll, False, False)
        self.hpaned.show_all()

        self.close_button = Button(stock=STOCK_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())

        self.terminal = terminal()
        self.terminal.connect("child-exited", lambda _: self.close_button.show())

        self.expander = Expander(_("Terminal"))
        self.expander.connect("notify::expanded", self._set_size)
        self.expander.show()

        self.vbox = VBox(False, 0)
        self.vbox.show()
        
        self.vbox.pack_start(self.hpaned, True, True, 0)
        self.vbox.pack_start(self.expander, False, False, 0)
        self.vbox.pack_start(self.close_button, False, False, 0)

        
        self.add(self.vbox)

    def run(self):

        self.show()
        self.terminal.do(self.queues)
        return

    def _stop_closing(self, widget, event):
        self.stop_emission("delete-event")
        return True

class local_install_fchooser_dialog(FileChooserDialog):

    def __init__(self, parent, icon):
        FileChooserDialog.__init__(self, _("Choose package to install"),
                                   parent, FILE_CHOOSER_ACTION_OPEN,
                                   (STOCK_OPEN, RESPONSE_ACCEPT,
                                    STOCK_CANCEL, RESPONSE_REJECT))
        self.set_icon(pixbuf_new_from_file(icon))

class local_confirm_dialog(confirm_dialog):

    def __init__(self, parent, fname, pacs_queue, icon):
        from os.path import basename
        
        confirm_dialog.__init__(self, parent, pacs_queue, icon)
        package = basename(fname)

        name_n_ver = package.rsplit("-", 3)
        name = name_n_ver.pop(0)
        del name_n_ver[-1]
        version = '-'.join(name_n_ver)
        
        model = self.install_tree.get_model()
        model.prepend(["red", name, version])

class local_install_dialog(do_dialog):

    def __init__(self, fname, pacs_queue, icon):
        from os.path import basename
        
        do_dialog.__init__(self, pacs_queue, icon)

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

    def __init__(self, parent, icon):

        Dialog.__init__(self, _("Search for.."), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

        self.set_icon(pixbuf_new_from_file(icon))
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

    def __init__(self, parent, to_upgrade, icon):

        Window.__init__(self, WINDOW_TOPLEVEL)
        self.set_property("skip-taskbar-hint", True)
        self.set_property("modal", True)
        self.set_transient_for(parent)
        self.set_property("destroy-with-parent", True)
        self.set_position(WIN_POS_CENTER_ON_PARENT)
        self.set_default_size (300, 300)

        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_tree(to_upgrade)
        self._setup_layout()

    def _setup_layout(self):
        self.vbox = VBox(False, 0)
        self.vbox.show()

        self.terminal = terminal()
        self.terminal.connect("child-exited", lambda _: self.close_button.show())
        
        self.expander = expander_new_with_mnemonic(_("_Terminal"))
        self.expander.set_expanded(False)
        self.expander.connect("notify::expanded", self._set_size)
        self.expander.show_all()
        
        self.close_button = Button(stock=STOCK_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())

        scr = ScrolledWindow()
        scr.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        scr.add(self.tree)
        scr.show_all()

        self.vbox.pack_start( scr, True, True, 0)
        self.vbox.pack_start( self.expander, False, False, 0)
        self.vbox.pack_start(self.close_button, False, False, 0)

        self.add(self.vbox)
        return

    def _set_size (self, widget, data=None, event=None):
        if self.expander.get_expanded():
            self.size = self.get_size()
            self.expander.add(self.terminal)
            self.terminal.show()
        else:
            self.expander.remove(self.terminal)
            self.resize(self.size[0], self.size[1])
        return

    def _setup_tree(self, pacs):
        self.tree = PacView(pacs)
    
    def run(self):
        self.show()
        self.terminal.do_upgrade()

class upgrade_confirm_dialog(Dialog):

    def __init__(self, parent, to_upgrade, icon):

        Dialog.__init__(self, _("Confirm Upgrade"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_tree(to_upgrade)
        self._setup_layout()
        
    def _setup_tree(self, pacs):

        self.tree = PacView( pacs)
        self.tree.show()

    def _setup_layout(self):

        self.label = Label(_("Are you sure yo want to upgrade those packages?\n"))
        self.label.show()

        self.set_default_size (300, 300)

        scr = ScrolledWindow()
        scr.set_policy("automatic", "automatic")
        scr.add(self.tree)
        scr.show()
        
        self.vbox.pack_start(self.label, False, False, 0)
        self.vbox.pack_start(scr, True, True, 0)

    def run(self):
        retcode = Dialog.run(self)
        self.destroy()

        if retcode == RESPONSE_ACCEPT:
            return True
        else:
            return False

class command_dialog(Window):

    def __init__(self, parent, icon):

        Window.__init__(self, WINDOW_TOPLEVEL)
        self.set_property("skip-taskbar-hint", True)
        self.set_property("destroy-with-parent", True)
        self.set_modal(True)
        self.set_transient_for( parent)
        self.set_position( WIN_POS_CENTER_ON_PARENT)

        self.vbox = VBox(False, 0)
        
        self.terminal = terminal()
        self.terminal.connect("child-exited",
                              lambda _: self.close_button.show())
        self.terminal.show()
        
        self.close_button = Button(stock=STOCK_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())

        self.vbox.pack_start(self.terminal, False, False, 0)
        self.vbox.pack_start(self.close_button, False, False, 0)
        self.vbox.show()

        self.add(self.vbox)

        self.set_icon(pixbuf_new_from_file(icon))

    def run(self, command, pacman = True):
        self.show()

        if pacman:
            self.terminal.execute( "pacman --noconfirm -%s \n" %command)
            self.terminal.execute( "exit \n")
        else:
            self.terminal.execute( command)
            self.terminal.execute( "exit \n")
            
class error_dialog(MessageDialog):

    def __init__(self, parent, msg, icon):

        MessageDialog.__init__(self, parent,
                               DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                               MESSAGE_ERROR, BUTTONS_CLOSE, msg)
        self.set_icon(pixbuf_new_from_file(icon))

class choose_pkgbuild_dialog(FileChooserDialog):

    def __init__(self, parent, icon):

        FileChooserDialog.__init__(self, _("Choose the buildscript"),
                                   parent, FILE_CHOOSER_ACTION_OPEN,
                                   (STOCK_OPEN, RESPONSE_ACCEPT,
                                    STOCK_CANCEL, RESPONSE_REJECT))
        self.set_icon(pixbuf_new_from_file(icon))

    def run(self):
        res = FileChooserDialog.run(self)
        if res == RESPONSE_ACCEPT:
            return self.get_filename()

class change_user_dialog(Dialog):

    def __init__(self, parent, icon):
        Dialog.__init__(self, _("Confirm makepkg as root"),
                        parent, DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_OK, RESPONSE_ACCEPT,
                         STOCK_CANCEL, RESPONSE_REJECT))

        self.add_button(_("Run as root"), 1000)
        
        lab = Label(_("Running makepkg as root is a bad idea.\nSelect an alternate user or confirm that you want to run it as root"))

        uname_frame = Frame(_("Username:"))
        pwd_frame = Frame(_("Password"))

        self.uname_entry = Entry()
        
        uname_frame.add(self.uname_entry)
        
        self.vbox.pack_start(lab)
        self.vbox.pack_start(uname_frame)
        self.vbox.show_all()

    def run(self):
        res = Dialog.run(self)
        if res == 1000:
            return "root"
        elif res == RESPONSE_ACCEPT:
            uname = self.uname_entry.get_text()
            return uname
        else:
            self.destroy()
            return "reject"
