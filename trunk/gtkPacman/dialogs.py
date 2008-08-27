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

from gtk import Dialog, MessageDialog, AboutDialog, FileChooserDialog
from gtk import Expander, ListStore, TreeView, HPaned, Frame, Label, Button
from gtk import Window, WINDOW_TOPLEVEL, WIN_POS_CENTER, VBox, Entry, HBox
from gtk import ScrolledWindow, VPaned, POLICY_AUTOMATIC, STOCK_STOP, ICON_SIZE_BUTTON
from gtk import CellRendererPixbuf, CellRendererText, Entry, Image
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

class ignorepkg_dialog(MessageDialog):

    def __init__(self, name, icon):
        name = str( name)
        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_QUESTION, BUTTONS_YES_NO,
                               _("Current package(s) are listed as IgnorePkg.\n%s\n Are you sure you want to continue?" %name[1:-1]))
        self.set_icon (pixbuf_new_from_file(icon))

class holdpkg_dialog(MessageDialog):

    def __init__(self, name, icon):

        MessageDialog.__init__(self, None,
                               DIALOG_MODAL, MESSAGE_INFO, BUTTONS_YES_NO,
                               _("Current package(s) are listed as HoldPkg.\n%s\nAre You sure you want to continue?") %name)
        self.set_icon (pixbuf_new_from_file(icon))

class warning_dialog(Dialog):

    def __init__(self, parent, pacs, icon, conflict=False):

        Dialog.__init__(self, _("Warning!"), parent,
                        DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                        (STOCK_YES, RESPONSE_YES, STOCK_NO, RESPONSE_REJECT))
        
        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_tree(pacs)
        self._setup_layout(conflict)

    def _setup_layout(self, conflict):

        self.set_default_size(-1,250)
        
        if not conflict:
            label = Label(_("These packages are required by package(s) you've selected for removal.\nDo you want to remove them all?"))
        else:
            label = Label("Package(s) that are about to be installed conflicts \nwith package(s) that are already installed.\nDo you want to remove them?")
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

    def __init__(self, parent, icon):
        from os.path import exists, abspath, join
        from gtk.gdk import pixbuf_new_from_file
        Dialog.__init__(self, None, parent)
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
        self.set_authors(["Stefano Esposito <stefano.esposito87@gmail.com>", "'Seti' <seti4ever@gmail.com>"])
        self.set_artists(["James D <jamesgecko@gmail.com>"])

        path = "/usr/share/gtkpacman/"
        if not exists(path):
            path = abspath("data/")
            
        fname = join(path, "icons/pacman.png")
        logo = pixbuf_new_from_file(fname)
        self.set_logo(logo)
        
class command_dialog(Dialog):
    """This is main window that will be later inherited by do_dialog
    """
    def __init__(self, parent, icon):

        Dialog.__init__(self, None, parent, DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT)
        self.set_icon(pixbuf_new_from_file(icon))
        
        self.close_button = self.add_button(STOCK_CLOSE, RESPONSE_CLOSE)
        self.close_button.connect("clicked", lambda _: self.destroy())
        
        self.terminal = terminal()
        self.terminal.connect("child-exited", lambda _: self.close_button.show())  
        
    def _setup_layout(self):

        self.vbox.pack_start(self.terminal, False, False, 0)
        
    def exit_terminal(self):
        pass

    def install(self, command, pacman = True):
        self._setup_layout()
        self.show_all()
        self.close_button.hide()

        if pacman:
            self.terminal.execute( "pacman --noconfirm -%s \n" %command)
            self.terminal.execute( "exit \n")
            self.terminal.execute( "exit \n")
        else:
            self.terminal.execute( command)
            self.terminal.execute( "exit \n")
        
    def run_su(self):
        self.terminal.init_su()
        
    def run_login(self, user_pass):
        self.terminal.login(user_pass)
        del user_pass

class do_dialog(command_dialog):

    def __init__(self, parent, icon, queues):

        command_dialog.__init__(self, parent, icon)

        self.queues = queues
        self._setup_trees(queues)
        self._setup_shared_widgets()
        self._setup_layout()

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
            
    def _setup_shared_widgets(self):
        
        self.expander = Expander(_("Terminal"))
        self.expander.set_expanded(False)
        self.expander.hide_all()
        self.expander.connect("notify::expanded", self._set_size)
        
        self.yes_button = self.add_button(STOCK_YES, RESPONSE_YES)
        self.no_button = self.add_button(STOCK_NO, RESPONSE_NO)

    def _setup_layout(self):

        self.set_default_size(600,200)
        label = Label(_("Are you sure you want to install/remove those packages?\n"))
        self.hpaned = HPaned()
        
        inst_scroll = ScrolledWindow()
        inst_scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)

        rem_scroll = ScrolledWindow()
        rem_scroll.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        
        inst_scroll.add(self.install_tree)
        rem_scroll.add(self.remove_tree)
        
        self.hpaned.pack1(inst_scroll, False, False)
        self.hpaned.pack2(rem_scroll, False, False)
    
        self.vbox.pack_start( label, False, False, 0 )
        self.vbox.pack_start( self.hpaned, True, True, 0 )
        self.vbox.pack_start( self.expander, False, False, 0 )
        
        self.show_all()
        self.expander.hide_all()
        self.close_button.hide()
        
    def install(self):
        self.expander.set_sensitive(True)
        self.yes_button.hide_all()
        self.no_button.hide_all()
        self.expander.show_all()
        self.terminal.do(self.queues)
    
class upgrade_dialog(do_dialog):

    def __init__(self, parent, icon, queue):

        do_dialog.__init__(self, parent, icon, queue)
        
    def _setup_trees(self, pacs):
        self.tree = PacView(pacs)

    def _setup_layout(self):
        self.set_default_size (300, 300)
        label = Label(_("Are you sure you want to upgrade those packages?\n"))
    
        scr = ScrolledWindow()
        scr.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        scr.add(self.tree)
        
        self.vbox.pack_start( label, False, False, 0)
        self.vbox.pack_start( scr, True, True, 0)
        self.vbox.pack_start( self.expander, False, False, 0)

        self.vbox.show_all()
        self.expander.hide_all()
        self.close_button.hide()
    def install(self):
        self.expander.set_sensitive(True)
        self.yes_button.hide_all()
        self.no_button.hide_all()
        self.expander.show_all()
        self.terminal.do_upgrade()

class local_install_fchooser_dialog(FileChooserDialog):

    def __init__(self, parent, icon):
        FileChooserDialog.__init__(self, _("Choose package to install"),
                                   parent, FILE_CHOOSER_ACTION_OPEN,
                                   (STOCK_OPEN, RESPONSE_ACCEPT,
                                    STOCK_CANCEL, RESPONSE_REJECT))
        self.set_icon(pixbuf_new_from_file(icon))

class local_install_dialog(do_dialog):

    def __init__(self, parent, icon, pacs_queue, fname):
        from os.path import basename
        
        do_dialog.__init__(self, parent, icon, pacs_queue)

        package = basename(fname)
        
        name_n_ver = package.rsplit("-", 3)
        name = name_n_ver.pop(0)
        del name_n_ver[-1]
        version = '-'.join(name_n_ver)
        
        model = self.install_tree.get_model()
        model.prepend(["red", name, version])

        #self.inst_model.prepend(["red", name, version])
        self.fname = fname
        self.pacs_queue = pacs_queue

    def install(self):
        self.expander.set_sensitive(True)
        self.yes_button.hide_all()
        self.no_button.hide_all()
        self.expander.show_all()
        self.terminal.do_local(self.fname, self.pacs_queue)
    
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
            
class error_dialog(MessageDialog):

    def __init__(self, parent, msg, icon):

        MessageDialog.__init__(self, parent,
                               DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                               MESSAGE_ERROR, BUTTONS_CLOSE, msg)
        self.set_icon(pixbuf_new_from_file(icon))
    
class password_dialog(Dialog):
    
    def __init__(self, parent, icon):
        Dialog.__init__(self, "GtkPacman Login", parent,
                               DIALOG_MODAL | DIALOG_DESTROY_WITH_PARENT,
                           (STOCK_OK, RESPONSE_ACCEPT, STOCK_CANCEL, RESPONSE_REJECT))
        self.set_icon(pixbuf_new_from_file(icon))
        self._setup_layout()
        
    def _setup_layout(self):
        self.password_entry = Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_invisible_char('*')
        info_label = Label(' Enter root password ')
        
        self.hbox = HBox()
                
        self.vbox.pack_start(info_label)
        self.vbox.pack_start(self.password_entry)
        self.vbox.pack_start(self.hbox)        
        self.show_all()
        
    def show_warning(self):
        image = Image()
        image.set_from_stock(STOCK_STOP, ICON_SIZE_BUTTON)
        warning_label = Label(' Invalid Password! ')        
        self.hbox.pack_start(image, False, False, 10)
        self.hbox.pack_start(warning_label, False, False, 0)
        self.show_all()

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
