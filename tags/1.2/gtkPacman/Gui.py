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
# gtkPacman is copyright (C)2005 by Stefano Esposito

import os
import gtk, gtk.glade, thread, time
from Configuration import *
from Pacman import *
from Terminal import *
from Preferences import *
from Models import *

try:
    from egg import trayicon
except:
    import trayicon
    
class gui:
    """Class that runs and manage the gui"""
    def __init__(self, fname, conf, icons):
        """Init the gui, the config, and the database"""
        
        self.gld = gtk.glade.XML(fname, "main_win", 'gtkPacman')

        hand_dict = { "quit":              self.quit,
                      "hide":              self.hide,
                      "preferences":       self.preferences,
                      "sync":              self.sync,
                      "refresh":           self.refresh,
                      "upgrade_sys":       self.upgrade_sys,
                      "add":               self.add,
                      "remove":            self.pac_remove,
                      "upgrade":           self.upgrade,
                      "about":             self.about,
                      "combobox":          self.combobox,
                      "cursor_changed":    self.cursor_changed,
                      "popup":             self.popup,
                      "dep_row":           self.dep_row_activated,
                      "pac_row":           self.pac_row_activated,
                      "reqby_row":         self.reqby_row_activated,
                      "menu_clear_cache":  self.clear_cache,
                      "menu_empty_cache":  self.empty_cache,
                      "expander"        :  self.expander }
        
        self.gld.signal_autoconnect(hand_dict)

        self.key_lab = None
        
        if os.getuid():
            self.areroot = False
            self.gld.get_widget("edit").set_sensitive(False)
                                    
        else:
            self.areroot = True

        self.configuration = configuration(conf, self.areroot)
        self.configuration.readfp(self.configuration.cfg)

        self.fname = fname
        self.stat_bar = self.gld.get_widget("statusbar")
        self.stat_cont = self.stat_bar.get_context_id("statusbar")
        self.prog_bar = self.gld.get_widget("prog_bar")
        self.prog_bar.reparent(self.stat_bar)
        self.stat_bar.set_child_packing(self.prog_bar, False, True, 0,
                                        gtk.PACK_START)
        
        self.make_icons(icons)
        self.icons = icons

        
        self.entry = self.gld.get_widget("pac_entry")
        self.filechooser = filechooser(self.gld.get_widget("hbox28"))
        self.butt = self.gld.get_widget("pac_butt")
        
        self.pac_tree = self.gld.get_widget("pac_tree")
        self.setup_pac_list()
        
        self.dep_tree = self.gld.get_widget("dep_tree")
        self.setup_dep_list()

        self.reqby_tree = self.gld.get_widget("req_by_tree")
        self.setup_req_by_list()

        self.dep_already_done = False
        self.dep_times = 0
        self.req_already_done = False
        self.req_times = 0
        
        self.pacman = database()
        
        
        self.combo = self.gld.get_widget("combobox")
        self.combo.set_model(combo_model(self.pacman))
        self.combo.set_active(0)

        self.terminal = terminal(self)

        self.tray = Tray(self, fname)
        
        if not self.areroot:
            dlg = gtk.MessageDialog(self.gld.get_widget("main_win"),
                                    gtk.DIALOG_MODAL |
                                    gtk.DIALOG_DESTROY_WITH_PARENT,
                                    gtk.MESSAGE_WARNING,
                                    gtk.BUTTONS_CLOSE,
                                    _("""You're not root. You won't be able to edit configuration. If you want to manage packages you'll be asked for root password time by time"""))
            dlg.run()
            dlg.destroy()
        self.set_stat_msg(_("Done"))

    def make_icons(self, icons):
        """Set stock icons for the app"""
        for icon_name in icons.keys():
            icon = gtk.gdk.pixbuf_new_from_file(icons[icon_name])
            icon_set = gtk.IconSet(icon)
            icon_factory = gtk.IconFactory()
            icon_factory.add(icon_name, icon_set)
            icon_factory.add_default()
        

    def quit(self, widget, event=None):
        """Quit the app"""
        gtk.main_quit()
        return

    def hide(self, widget, event=None):
        self.gld.get_widget("main_win").hide()
        return True

    def clear_cache(self, event):
        """Clear packages cache"""
        self.terminal.do(self.areroot, "S", "-c", None, _("Clearing cache"))
        return

    def empty_cache(self, event):
        """Empty the package's cache"""
        self.terminal.do(self.areroot, "S", "-cc", None, _("Emptying cache"))
        return
    
    def preferences(self, event):
        """Calls the pref dialog"""
        pref_dialog(self.fname, self.configuration, self.terminal)
        return

    def pac_row_activated(self, event=None, widget=None, path=None):
        """Called when user double clicks on a row in the pac list."""
        selection = self.pac_tree.get_selection()
        self.sync(selection)
        return

    def dep_row_activated(self, event=None, widget=None, path=None):
        """Called when user double clicks on a row in the deps list"""
        selection = self.dep_tree.get_selection()
        self.sync(selection)
        return

    def reqby_row_activated(self, event=None, widget=None, path=None):
        selection = self.reqby_tree.get_selection()
        self.sync(selection)
        
    def sync(self, event, widget=None, path=None):
        """Install or upgrade a package using pacman"""
        if type(event) == type(gtk.TreeSelection()):
            selection = event
        else:
            selection = self.pac_tree.get_selection()

        if selection.count_selected_rows():
            args = self.configuration.get_common_pref(True)
            args = " ".join((args, self.configuration.get_x_pref("sync")))
            (model, it) = selection.get_selected()
            name = model.get_value(it, 1)
            self.terminal.do(self.areroot, "S", args, name)
        else:
            self.entry_id = self.entry.connect("activate", self.get_name, "S")
            self.butt_id = self.butt.connect("clicked", self.get_name, "S")
            self.entry.show()
            self.butt.show()
        return

    def set_stat_msg(self, msg):
        try:
            self.stat_bar.pop(self.stat_cont)
        except Exception:
            pass
        
        self.stat_bar.push(self.stat_cont, msg)
        return
        

    def refresh(self, event=None):
        """Refresh local repos"""
        self.terminal.do(self.areroot, "S", "-y", None,
                         _("Refreshing Database"))
        return

    def upgrade_sys(self, event=None):
        """Upgrade the system using pacman"""
        args = self.configuration.get_common_pref(True)
        args = " ".join((args, self.configuration.get_x_pref("sync")))
        args = " ".join((args, "-u"))
        self.terminal.do(self.areroot, "S", args, None, _("Upgrading System"))
        return

    def add(self, event):
        """Add a package to the system, using pacman"""
        self.butt_id = self.butt.connect("clicked", self.get_name, "A")
        self.filechooser.show()
        self.butt.show()
        return

    def pac_remove(self, event):
        selection = self.pac_tree.get_selection()
        self.remove(selection)

    def dep_remove(self, event):
        selection = self.dep_tree.get_selection()
        self.remove(selection)

    def reqby_remove(self, event):
        selection = self.reqby_tree.get_selection()
        self.remove(selection)

    def remove(self, selection):
        """Remove a package from the system using pacman"""
        if selection.count_selected_rows():
            (model, it) = selection.get_selected()
            name = model.get_value(it, 1)
            if self.pacman.get_by_name(name).get_installed():
                args = self.configuration.get_common_pref()
                args = " ".join((args, self.configuration.get_remove_pref()))
                self.terminal.do(self.areroot, "R", args, name)
            else:
                error_dlg(self.gld.get_widget("main_win"),
                          _("Package %s isn't installed") %name)
        else:
            self.entry_id = self.entry.connect("activate", self.get_name, "R")
            self.butt_id = self.butt.connect("clicked", self.get_name, "R")
            self.entry.show()
            self.butt.show()
        return

    def upgrade(self, event):
        """Upgrade a package from a local file"""
        self.butt_id = self.butt.connect("clicked", self.get_name, "U")
        self.filechooser.show()
        self.butt.show()
        return

    def get_name(self, event, what):
        """Get the name inserted by the user in the input line, and do the
        desired action"""
        if what == "A" or what == "U":
            name = self.filechooser.get_filename()
            self.filechooser.unselect_all()
            self.filechooser.hide()
        else:
            name = self.entry.get_text()
            self.entry.set_text("")
            self.entry.hide()
            self.entry.disconnect(self.entry_id)
            
        self.butt.hide()
        self.butt.disconnect(self.butt_id)
        
        args = self.configuration.get_common_pref()

        if what == "S":
            args = " ".join((args, self.configuration.get_x_pref("sync")))
            args = " ".join((args, self.configuration.get_refresh()))
            try:
                self.pacman.get_by_name(name)
            except NameError:
                if name == "":
                    mess = _("Please, insert a package name")
                else:
                    mess = _("Package %s doesn't exist in the database") %name

                error_dlg(self.gld.get_widget("main_win"), mess)
                return
        
        elif what == "R":
            args = " ".join((args, self.configuration.get_remove_pref()))
            try:
                self.pacman.get_by_name(name)
            except NameError:
                if name == "":
                    mess = _("Please, insert a package name")
                else:
                    mess = _("Package %s doesn't exist in the database") %name

                error_dlg(self.gld.get_widget("main_win"), mess)
                return
            if not self.pacman.get_by_name(name).get_installed():
                error_dlg(self.gld.get_widget("main_win"),
                          _("Package %s is not installed") %name)
                return

        elif what == "F":
            if not name:
                return
            else:
                try:
                    packs = self.pacman.get_by_keywords(name)
                except ValueError:
                    error_dlg(self.gld.get_widget("main_win"),
                              _("No package find with this keyword: %s") %name)
                    return
                if packs:
                    self.pac_tree.set_model(pac_model(self.pacman, packs))
                else:
                    self.pac_tree.set_model()
                hbox = self.gld.get_widget("hbox27")
                self.key_lab = gtk.Label(name)
                hbox.pack_start(self.key_lab)
                self.key_lab.show()
                return

        else:
            if what == "A":
                args = " ".join((args, self.configuration.get_x_pref("add")))
            elif what == "U":
                args = " ".join((args, self.configuration.get_x_pref("up")))

        self.terminal.do(self.areroot, what, args, name)
        return

    def about(self, event):
        """Runs the about dialog"""
        about_dlg(self.fname)
        return

    def combobox(self, event):
        """Called when the users changes the selected voice in the combobox"""
        if self.key_lab:
            self.key_lab.destroy()
            self.key_lab = None
        combo = self.gld.get_widget("combobox")
        active = combo.get_active()
        if active == 0:
            self.pac_tree.set_model(pac_model(self.pacman))
        elif active == 11:
            self.entry_id = self.entry.connect("activate", self.get_name, "F")
            self.butt_id = self.butt.connect("clicked", self.get_name, "F")
            self.entry.show()
            self.butt.show()
        elif active == 4:
            orphans = self.pacman.get_orphans()
            self.pac_tree.set_model(pac_model(self.pacman, orphans))
        else:
            if active == 1:
                col = "Installed"
            elif active == 2:
                col = "Not installed"
            elif active == 3:
                col = "To upgrade"
            elif active == 10:
                col = "Manually installed"
            else:
                model = combo.get_model()
                it = combo.get_active_iter()
                col = model.get_value(it, 0)
                
            self.pac_tree.set_model(pac_model(self.pacman, col.lower()))
            
        return
    
    def cursor_changed(self, event):
        """Called when the user moves the cursor in the pac list"""
        (model, it) = self.pac_tree.get_selection().get_selected()
        name = model.get_value(it, 1)
        self.dep_tree.set_model(dep_model(self.pacman, name, self.gld))
        try:
            pac = self.pacman.get_by_name(name)
        except NameError:
            print _("This is probably a bug.\n\
            Plaese report it at http://gna.org/projects/gtkpacman")
            raise
            
        desc = pac.get_description()
        buff = self.gld.get_widget("description").get_buffer()
        buff.set_text(name.upper() + ":\n" + desc)
        if pac.get_installed():
            buff = self.gld.get_widget("filelist").get_buffer()
            buff.set_text(pac.get_filelist())
            self.reqby_tree.set_model(req_by_model(self.pacman, name))
        else:
            self.gld.get_widget("filelist").get_buffer().set_text(
                _("%s is not installed") %str(name).upper())
            self.reqby_tree.set_model()
        return

    def select_pac(self, model, path, iter, data):
        if data[1] == "dep" and self.dep_already_done:
            return True
        if data[1] == "req" and self.req_already_done:
            return True

        pac_name = model.get_value(iter, 1)
        print data[0], pac_name
        if pac_name == data[0]:
            self.pac_tree.set_cursor(path, self.pac_tree.get_column(1))
            return True

        return False

    def popup(self, widget, event):
        """Pops up the popup menu in the pac or dep list"""
        if event.button == 3:
            gl = gtk.glade.XML(self.fname, "popup_menu")
            name = gtk.glade.get_widget_name(widget)
            hand_dict = { "on_add"     : self.add,                          
                          "on_upgrade" : self.upgrade,
                          "on_up_sys"  : self.upgrade_sys,
                          "on_refr_db" : self.refresh }
            
            if name == "pac_tree":
                hand_dict["on_remove"] = self.pac_remove
                hand_dict["on_sync"] = self.pac_row_activated
                
            elif name == "dep_tree":
                hand_dict["on_remove"] = self.dep_remove
                hand_dict["on_sync"] = self.dep_row_activated
                
            elif name == "reqby_tree":
                hand_dict["on_remove"] = self.reqby_remove
                hand_dict["on_sync"] = self.reqby_row_activated
                
            
            gl.signal_autoconnect(hand_dict)
            gl.get_widget("popup_menu").popup(None,
                                              None,
                                              None,
                                              event.button,
                                              event.get_time())
        return

    def setup_pac_list(self):
        """Setup the pac treeview, setting columns and attributes"""
        self.pac_tree.insert_column_with_attributes(-1,
                                                    "",
                                                    gtk.CellRendererPixbuf(),
                                                    stock_id=0)
        self.pac_tree.insert_column_with_attributes(-1,
                                                    _("Package"),
                                                    gtk.CellRendererText(),
                                                    text=1)
        
        self.pac_tree.insert_column_with_attributes(-1,
                                                    _("Version"),
                                                    gtk.CellRendererText(),
                                                    text=2)
        self.pac_tree.insert_column_with_attributes(-1,
                                                    _("Installed Version"),
                                                    gtk.CellRendererText(),
                                                    text=3)
        self.pac_tree.insert_column_with_attributes(-1,
                                                    _("Repository"),
                                                    gtk.CellRendererText(),
                                                    text=4)
        col_num = 0
        for col in self.pac_tree.get_columns():
            col.set_resizable(True)
            col.set_clickable(True)
            col.set_reorderable(True)
            col.set_sort_indicator(True)
            col.set_sort_column_id(col_num)
            col_num += 1
        return
            
    def setup_dep_list(self):
        """Setup the dependencies list, setting columns and attributes"""
        self.dep_tree.insert_column_with_attributes(-1,
                                                    "",
                                                    gtk.CellRendererPixbuf(),
                                                    stock_id=0)
        self.dep_tree.insert_column_with_attributes(-1,
                                                    _("Package"),
                                                    gtk.CellRendererText(),
                                                    text=1)

        self.dep_tree.insert_column_with_attributes(-1,
                                                    _("Repository"),
                                                    gtk.CellRendererText(),
                                                    text=2)
        col_num = 0
        for col in self.dep_tree.get_columns():
            col.set_resizable(True)
            col.set_clickable(True)
            col.set_reorderable(True)
            col.set_sort_indicator(True)
            col.set_sort_column_id(col_num)
            col_num += 1
        return

    def setup_req_by_list(self):
        self.reqby_tree.insert_column_with_attributes(-1,
                                                      "",
                                                      gtk.CellRendererPixbuf(),
                                                      stock_id=0)
        self.reqby_tree.insert_column_with_attributes(-1,
                                                      _("Package"),
                                                      gtk.CellRendererText(),
                                                      text=1)
        self.reqby_tree.insert_column_with_attributes(-1,
                                                      _("Repository"),
                                                      gtk.CellRendererText(),
                                                      text=2)
        col_num = 0
        for col in self.reqby_tree.get_columns():
            col.set_resizable(True)
            col.set_clickable(True)
            col.set_reorderable(True)
            col.set_sort_indicator(True)
            col.set_sort_column_id(col_num)
            col_num += 1
        return

    def expander(self, expander):
        if(expander.get_expanded()):
            #self.gld.get_widget("vpaned1").set_position(180)
            expander.parent.set_position(350)
        else:
            #self.gld.get_widget("vpaned1").set_position(320)
            expander.parent.set_position(180)
        return

    def bar(self, bar, terminal):
        gtk.threads_enter()
        self.prog_bar.show()
        while 1:
            try:
                is_visible = self.gld.get_widget("expander").visible
            except Exception:
                print "Ah-ah!"
                return
            
            if not is_visible:
                self.prog_bar.hide()
                break
            self.prog_bar.pulse()
        gtk.threads_leave()

    def refresh_db(self, db):
        self.pacman = db
        return

    def start_pulse(self):
        self.pulse = 1
        thread.start_new_thread(self.do_pulse, ())
        return

    def stop_pulse(self):
        self.pulse = 0
        return

    def do_pulse(self):
        while self.pulse:
            gtk.threads_enter()
            self.gld.get_widget("prog_bar").pulse()
            gtk.threads_leave()
            time.sleep(0.5)
        self.gld.get_widget("prog_bar").set_fraction(1.0)
        return
            
    def run(self):
        """Runs the main loop"""
        gtk.main()
        return
    
class error_dlg(gtk.MessageDialog):
    """Runs an error dialog"""
    def __init__(self, parent, message):
        """Runs the dialog with the given message, using the given wid
        as parent"""
        gtk.MessageDialog.__init__(self,
                                   parent,
                                   gtk.DIALOG_MODAL |
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_CLOSE,
                                   message)

        self.run()
        self.destroy()
        return

class about_dlg:
    """Runs the about dialog"""
    def __init__(self, fname):

        self.gld = gtk.glade.XML(fname, "about_dlg", "gtkPacman")
        self.dlg = self.gld.get_widget("about_dlg")
        self.dlg.set_version("1.2")
        self.dlg.run()
        self.dlg.destroy()
        return

class filechooser(gtk.FileChooserButton):

    def __init__(self, hbox):

        gtk.FileChooserButton.__init__(self, "Select a Package")
        self.add_filters()

        self.set_width_chars(76)
        hbox.pack_start(self, False, True, 0)
        hbox.reorder_child(self, 1)

    def add_filters(self):
        
        pkgfilter = gtk.FileFilter()
        pkgfilter.add_pattern("*.pkg.tar.gz")
        pkgfilter.set_name("Packages")
        self.add_filter(pkgfilter)

        allfilter = gtk.FileFilter()
        allfilter.add_pattern("*")
        allfilter.set_name("All files")
        self.add_filter(allfilter)
        return

class Tray(trayicon.TrayIcon):

    def __init__(self, gui, fname):

        trayicon.TrayIcon.__init__(self, "gtkPacman")
        
        self.p_window = gui.gld.get_widget("main_win")
        self.gui = gui
        
        self.icon = gtk.image_new_from_stock("pacman",
                                             gtk.ICON_SIZE_SMALL_TOOLBAR)
        
        self.event_box = gtk.EventBox()
        self.event_box.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                                  gtk.gdk.POINTER_MOTION_MASK | 
                                  gtk.gdk.POINTER_MOTION_HINT_MASK |
                                  gtk.gdk.CONFIGURE)
        self.event_box.add(self.icon)
        
        self.gld = gtk.glade.XML(fname, "tray_popup_menu", "gtkPacman")
        hand_dict = { "popup_up_sys" : gui.upgrade_sys,
                      "popup_refr_db": gui.refresh,
                      "on_add":        gui.add,
                      "on_upgrade":    gui.upgrade,
                      "on_quit":       gui.quit,
                      "on_show":       self.on_show }
        self.gld.signal_autoconnect(hand_dict)

        self.event_box.connect("button_press_event", self.button_press)
        self.add(self.event_box)
        self.show_all()
        return

    def button_press(self, widget, event):

        if event.button == 1:
            self.show_hide()
                
        if event.button == 3:
            
            self.gld.get_widget("tray_popup_menu").popup(None,
                                                         None,
                                                         None,
                                                         event.button,
                                                         event.get_time())
        return
    
    def on_show(self, widget):

        if widget.get_active():
            self.p_window.show()
        else:
            self.p_window.hide()
        return

    def show_hide(self):

        if self.p_window.get_property("visible"):
            self.p_window.hide()
            self.gld.get_widget("show_window").set_active(False)

        else:
            self.p_window.show()
            self.gld.get_widget("show_window").set_active(True)
            
        return
    
