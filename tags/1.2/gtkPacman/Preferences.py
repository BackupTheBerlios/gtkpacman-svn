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

import gtk, gtk.glade, gtk.gdk, os
from Configuration import *

class pref_dialog:
    """Runs the preferences dialog"""
    def __init__(self, fname, configuration, terminal):
        """Init the dialog"""
        self.gld = gtk.glade.XML(fname, "pref_dlg")
        hand_dict = { "alt_root" : self.alt_root,
                      "alt_db"   : self.alt_db,
                      "alt_conf" : self.alt_conf }
        self.gld.signal_autoconnect(hand_dict)
        
        self.config = configuration
        self.terminal = terminal
        #To each widget name corresponds a section and option
        self.options = { "pref_refr_chk":           { "section": "common",
                                                      "option": "refresh"},
                         "pref_alt_root_chk":       { "section": "common",
                                                      "option":"use_alt_root"},
                         "pref_alt_root_entry":     { "section": "common",
                                                      "option": "alt_root"},
                         "pref_alt_db_chk":         { "section": "common",
                                                      "option": "use_alt_db"},
                         "pref_alt_db_entry":       { "section": "common",
                                                      "option": "alt_db" },
                         "pref_alt_conf_chk":       { "section": "common",
                                                     "option":"use_alt_conf"}, 
                         "pref_alt_conf_entry":     { "section": "common",
                                                      "option": "alt_conf"},
                         "pref_verbose_chk":        { "section": "common",
                                                      "option": "verbose" },
                         "pref_sync_dep_chk":       { "section": "sync",
                                                      "option": "dep_check" },
                         "pref_sync_force_chk":     { "section": "sync",
                                                      "option": "force" },
                         "pref_sync_noconfirm_chk": { "section": "sync",
                                                      "option": "noconfirm" },
                         "pref_sync_down_only_chk": { "section": "sync",
                                                      "option": "down_only"},
                         "pref_rem_dep_chk" :       { "section": "remove",
                                                      "option": "dep_check" },
                         "pref_rem_cascade_chk":    { "section": "remove",
                                                      "option": "cascade" },
                         "pref_rem_recursive_chk":  { "section": "remove",
                                                      "option": "recursive" },
                         "pref_rem_dbonly_chk":     { "section": "remove",
                                                      "option": "db_only" },
                         "pref_rem_nosave_chk":     { "section": "remove",
                                                      "option": "nosave" },
                         "pref_add_dep_chk":        { "section": "add",
                                                      "option": "dep_check" },
                         "pref_add_force_chk":      { "section": "add",
                                                      "option": "force" },
                         "pref_add_noconfirm_chk":  { "section": "add",
                                                      "option": "noconfirm" },
                         "pref_up_dep_chk":         { "section": "up",
                                                      "option": "dep_check" },
                         "pref_up_force_chk":       { "section": "up",
                                                      "option": "force" },
                         "pref_up_noconfirm_chk":   { "section": "up",
                                                      "option": "noconfirm" },
                         "pref_gui_interm_bold":    { "section": "gui",
                                                      "option": "term_bold" },
                         "pref_gui_interm_scroll_out":{"section": "gui",
                                                       "option": "scroll_out"},
                         "pref_gui_interm_scroll_key":{"section": "gui",
                                                       "option": "scroll_key"},
                         "pref_gui_interm_backcol": { "section": "gui",
                                                      "option": "term_bcol"},
                         "pref_gui_interm_forecol": { "section": "gui",
                                                      "option": "term_fcol"},
                         "pref_gui_interm_backfile": { "section": "gui",
                                                       "option": "term_bfile"},
                         "pref_gui_interm_scrllns":{"section": "gui",
                                                    "option": "term_scr_lns"},
                         "pref_gui_interm_font": { "section": "gui",
                                                   "option": "term_font" }}
        
        self.dlg = self.gld.get_widget("pref_dlg")
        self.setup()
        response = self.dlg.run()

        if response == gtk.RESPONSE_OK:
            self.ok()
            self.dlg.destroy()
            
        else:
            self.dlg.destroy()
    
    def alt_root(self, event):
        """When toggled alt_root_chk sets alt_root_entry sensitive or
        insensitive"""
        entry = self.gld.get_widget("pref_alt_root_entry")
        if self.gld.get_widget("pref_alt_root_chk").get_active():
            entry.set_sensitive(True)
            
        else:
            entry.set_sensitive(False)
            

    def alt_db(self, event):
        """When toggled alt_db_chk, sets alt_db_entry sensitive or
        insensitive"""
        entry = self.gld.get_widget("pref_alt_db_entry")
        if self.gld.get_widget("pref_alt_db_chk").get_active():
            entry.set_sensitive(True)
            
        else:
            entry.set_sensitive(False)
            

    def alt_conf(self, event):
        """When toggled alt_conf_chk sets alt_conf_entry sensitive or
        insensitive"""
        entry = self.gld.get_widget("pref_alt_conf_entry")
        if self.gld.get_widget("pref_alt_conf_chk").get_active():
            entry.set_sensitive(True)
            
        else:
            entry.set_sensitive(False)
            
    def ok(self):
        """Sets the options in the config file to the desired values"""
        widgets = self.gld.get_widget_prefix("pref")
        for wid in widgets:
            key = gtk.glade.get_widget_name(wid)
            if type(wid) == type(gtk.CheckButton()):
                if wid.get_active():
                    self.config.set_option(self.options[key], "yes")
                else:
                    self.config.set_option(self.options[key], "no")
            elif type(wid) == type(gtk.Entry()):
                if wid.state != gtk.STATE_INSENSITIVE:
                    self.config.set_option(self.options[key], wid.get_text())
                    wid.set_text("")
                else:
                    self.config.set_option(self.options[key], "")
                    wid.set_text("")
            elif type(wid) == type(gtk.ColorButton()):
                if key == "pref_gui_interm_backcol":
                    back_col = wid.get_color()
                    self.config.set_option(self.options[key],
                                           self.parse_col(back_col))
                    self.terminal.set_color_background(back_col)
                elif key == "pref_gui_interm_forecol":
                    fore_col = wid.get_color()
                    self.config.set_option(self.options[key],
                                           self.parse_col(fore_col))
                    self.terminal.set_color_foreground(fore_col)
            elif type(wid) == type(gtk.FileChooserButton("s")):
                fname = wid.get_filename()
                if fname:
                    self.config.set_option(self.options[key],
                                           fname)
                    self.terminal.set_background_image_file(fname)
            elif type(wid) == type(gtk.SpinButton()):
                val = int(wid.get_value())
                self.config.set_option(self.options[key], str(val))
                self.terminal.set_scrollback_lines(val)
            elif type(wid) == type(gtk.FontButton()):
                font = wid.get_font_name()
                self.config.set_option(self.options[key], font)
                self.terminal.set_font_from_string(font)
        self.config.cfg.seek(0)
        self.config.write(self.config.cfg)
        return

    def setup(self):
        """Grab options from config file and sets pref dialog widgets to the
        proper value"""
        if self.config.get_value("refresh", "common"):
            self.gld.get_widget("pref_refr_chk").set_active(True)

        if self.config.get_value("verbose", "common"):
            self.gld.get_widget("pref_verbose_chk").set_active(True)
            
        if self.config.get_value("use_alt_root", "common"):
            self.gld.get_widget("pref_alt_root_chk").set_active(True)
            entry_txt = self.config.get_value("alt_root", "common", "string")
            self.gld.get_widget("pref_alt_root_entry").set_text(entry_txt)
            
        if self.config.get_value("use_alt_db", "common"):
            self.gld.get_widget("pref_alt_db_chk").set_active(True)
            entry_txt = self.config.get_value("alt_db", "common", "string")
            self.gld.get_widget("pref_alt_db_entry").set_text(entry_txt)

        if self.config.get_value("use_alt_conf", "common"):
            self.gld.get_widget("pref_alt_conf_chk").set_active(True)
            entry_txt = self.config.get_value("alt_conf", "common", "string")
            self.gld.get_widget("pref_alt_conf_entry").set_text(entry_txt)

        if not self.config.get_value("dep_check", "sync"):
            self.gld.get_widget("pref_sync_dep_chk").set_active(False)

        if self.config.get_value("force", "sync"):
            self.gld.get_widget("pref_sync_force_chk").set_active(True)

        if self.config.get_value("verbose", "sync"):
            self.gld.get_widget("pref_sync_verbose_chk").set_active(True)

        if self.config.get_value("noconfirm", "sync"):
            self.gld.get_widget("pref_sync_noconfirm_chk").set_active(True)

        if self.config.get_value("down_only", "sync"):
            self.gld.get_widget("pref_sync_down_only_chk").set_active(True)

        if not self.config.get_value("dep_check", "remove"):
            self.gld.get_widget("pref_rem_dep_chk").set_active(False)

        if self.config.get_value("verbose", "remove"):
            self.gld.get_widget("pref_rem_verbose_chk").set_active(True)

        if self.config.get_value("cascade", "remove"):
            self.gld.get_widget("pref_rem_cascade_chk").set_active(True)

        if self.config.get_value("recursive", "remove"):
            self.gld.get_widget("pref_rem_recursive_chk").set_active(True)

        if self.config.get_value("db_only", "remove"):
            self.gld.get_widget("pref_rem_dbonly_chk").set_active(True)

        if self.config.get_value("nosave", "remove"):
            self.gld.get_widget("pref_rem_nosave_chk").set_active(True)

        if not self.config.get_value("dep_check", "add"):
            self.gld.get_widget("pref_add_dep_chk").set_active(False)

        if self.config.get_value("force", "add"):
            self.gld.get_widget("pref_add_force_chk").set_active(True)

        if self.config.get_value("verbose", "add"):
            self.gld.get_widget("pref_add_verbose_chk").set_active(True)

        if self.config.get_value("noconfirm", "add"):
            self.gld.get_widget("pref_add_noconfirm_chk").set_active(True)

        if not self.config.get_value("dep_check", "up"):
            self.gld.get_widget("pref_add_dep_chk").set_active(False)

        if self.config.get_value("force", "up"):
            self.gld.get_widget("pref_add_force_chk").set_active(True)

        if self.config.get_value("verbose", "up"):
            self.gld.get_widget("pref_add_verbose_chk").set_active(True)

        if self.config.get_value("noconfirm", "up"):
            self.gld.get_widget("pref_add_noconfirm_chk").set_active(True)

        if self.config.get_value("term_bold", "gui"):
            self.gld.get_widget("pref_gui_interm_bold").set_active(True)

        if self.config.get_value("scroll_out", "gui"):
            self.gld.get_widget("pref_gui_interm_scroll_out").set_active(True)

        if self.config.get_value("scroll_key", "gui"):
            self.gld.get_widget("pref_gui_interm_scroll_key").set_active(True)

        hcol = self.config.get_value("term_bcol", "gui", "string")
        bcol = gtk.gdk.color_parse(hcol)
        self.gld.get_widget("pref_gui_interm_backcol").set_color(bcol)

        hcol = self.config.get_value("term_fcol", "gui", "string")

        fcol = gtk.gdk.color_parse(hcol)
        self.gld.get_widget("pref_gui_interm_forecol").set_color(fcol)

        fname = os.path.abspath(
            self.config.get_value("term_bfile", "gui", "string"))
        self.gld.get_widget("pref_gui_interm_backfile").set_filename(fname)

        scr_lns = self.config.get_value("term_scr_lns", "gui", "string")
        self.gld.get_widget("pref_gui_interm_scrllns").set_value(float(scr_lns))

        font = self.config.get_value("term_font", "gui", "string")
        self.gld.get_widget("pref_gui_interm_font").set_font_name(font)

    def parse_col(self, col):
        """Put the given gtk.gdk.Color in hex form"""
        hex_col = "#"
        red = hex(col.red)
        green = hex(col.green)
        blue = hex(col.blue)
        hex_col = "".join((hex_col,red[2:4],green[2:4],blue[2:4]))
        return hex_col
