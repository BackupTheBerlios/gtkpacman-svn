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

import gtk, atk, vte, os
import thread

class terminal(vte.Terminal):
    """Define a terminal widget"""
    def __init__(self, gui):
        """Init the terminal. Grab preferences from conf file and sets term's
        properties properly"""
        vte.Terminal.__init__(self)
        self.set_emulation("xterm")
        self.set_size(25, 5)
        self.connect("child-exited", self.exited)

        vbox = gui.gld.get_widget("vbox32")
        vbox.pack_end(self, True, True, 0)

        self.pacman = gui.pacman
        self.gld = gui.gld
        self.gui = gui
        
        self.conf = gui.configuration
        back_col = self.conf.get_value("term_bcol", "gui", "string")
        if back_col:
            color = gtk.gdk.color_parse(back_col)
        else:
            color = gtk.gdk.color_parse("#000000")
            
        self.set_color_background(gtk.gdk.color_parse(back_col))
        scr_lns = self.conf.get_value("term_scr_lns", "gui", "int")
        self.set_scrollback_lines(scr_lns)
        self.set_scroll_on_output(self.conf.get_value("scroll_out", "gui"))
        self.set_scroll_on_keystroke(self.conf.get_value("scroll_key", "gui"))
        font = self.conf.get_value("term_font", "gui", "string")
        if not font:
            font = "console 12"
        self.set_font_from_string(font)
        b_img = self.conf.get_value("term_bfile", "gui", "string")
        if b_img:
            self.set_background_image_file(b_img)
        

    def do(self, areroot, action, args=None, name=None, msg=None):
        """Execute the desired command"""
        if not areroot:
            command = "su -c \"pacman --noconfirm"
        else:
            command = "pacman --noconfirm"

        if action == "S":
            if name:
                if args:
                    command = " ".join((command, "-S", args, name))
                else:
                    command = " ".join((command, "-S", name))
                msg = _("Installing/Upgrading %s") %name
            else:
                command = " ".join((command, "-S", args))
                
        if action == "U":
            if name:
                if args:
                    command = " ".join((command, "-U", args, name))
                else:
                    command = " ".join((command, "-U", name))
            else:
                raise ValueError, _("U action requires a package argument")
            msg = _("Upgrading %s from local file") %name

        if action == "A":
            if name:
                if args:
                    command = " ".join((command, "-A", args, name))
                else:
                    command = " ".join((command, "-A", name))
            else:
                raise ValueError, _("A action requires a package argument")
            msg = _("Installing %s from local file") %name

        if action == "R":
            if name:
                if args:
                    command = " ".join((command, "-R", args, name))
                else:
                    command = " ".join((command, "-R", name))
            else:
                raise ValueError, _("R action requires a package argument")
            msg = _("Removing %s") %name

        if not areroot:
            command = command + "\""

        self.show()
        self.parent.show()
        self.gld.get_widget("prog_bar").show()
        self.fork_command()
        self.feed_child(command+";exit \n")       
        return

    def exited(self, widget):
        """When a command exited, refresh the database to reflect changes"""
        
        path = (self.gui.pac_tree.get_cursor())[0]
        vadj = self.gui.gld.get_widget("scrolledwindow5").get_vadjustment()
        value = vadj.get_value()

        model = self.gui.pac_tree.get_model()
        model.refresh(self.gui)

        if path:
            self.gui.pac_tree.set_cursor(path)
            vadj.set_value(value)

        self.parent.show_all()
        self.gui.gld.get_widget("term_close_butt").connect("clicked",
                                                           self.close)
        self.feed(_("Click button to close terminal"))
        self.gui.stop_pulse()
        self.gui.set_stat_msg(_("Done"))
        return


    
