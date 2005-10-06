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

import gtk, gtk.glade
from Pacman import *

class pac_model(gtk.ListStore):
    """Define a model for the pac list"""
    def __init__(self, pacman, col=None):
        """Init the model"""
        gtk.ListStore.__init__(self, str, str, str, str, str)
        self.pacman = pacman
        self.col = col
        self.parse_col()
        
    def refresh(self, gui):
        """Refresh the model"""
        self.pacman = database()
        gui.refresh_db(self.pacman)
        self.parse_col()

    def parse_col(self):
        """Parse the given col and set it to a proper value"""
        if self.col:
            if self.col == "to upgrade":
                self.show_old()
                return
            if self.col == "manually installed":
                self.col = "no_col"
            if self.col == "not installed":
                self.show_uninstalled()
                return
            if self.col == "installed":
                self.show_installed()
                return

            self.set_content(self.col)

        else:
            for col in self.pacman.cols:
                self.set_content(col)



    def set_content(self, col):
        """Sets the model content"""
        if type(col) == type(list()):
            for pac in col:
                image = ""
                if pac.get_isold():
                    image = "yellow"
                elif pac.get_installed():
                    image = "green"
                else:
                    image = "red"

                name = pac.get_name()
                version = pac.get_version()
                inst_ver = pac.get_inst_ver()
                col = pac.get_collection()
                self.append([image, name, version, inst_ver, col])

        else:
            for pac in self.pacman[col]:
                if col == "no_col":
                    repo = "-"
                else:
                    repo = col
                    
                image = ""
                if pac.get_isold():
                    image = "yellow"
                elif pac.get_installed():
                    image = "green"
                else:
                    image = "red"
                    
                name = pac.get_name()
                version = pac.get_version()
                inst_ver = pac.get_inst_ver()
                self.append([image, name, version, inst_ver, repo])
        return

    def show_old(self):
        """Set the model content to old packages"""
        olds = self.pacman.get_olds()
        if not olds:
            self.pacman.set_olds()
            olds = self.pacman.get_olds()
        if not olds:
            return
        image = "yellow"
        for pac in olds:
            self.append([image, pac.get_name(), pac.get_version(),
                         pac.get_inst_ver(), pac.get_collection()])
        return  
    def show_installed(self):
        """Set the model content to installed packages"""
        for col in self.pacman.cols:
            for pac in self.pacman[col]:
                if pac.get_installed():
                    image = "green"
                    if pac.get_isold():
                        image = "yellow"
                    name = pac.get_name()
                    version = pac.get_version()
                    inst_ver = pac.get_inst_ver()
                    col = pac.get_collection()
                    self.append([image, name, version, inst_ver, col])
        for pac in self.pacman["no_col"]:
            name = pac.get_name()
            version = pac.get_version()
            self.append(["green", name, version, version, "-"])
        return
    
    def show_uninstalled(self):
        """Set the model content to not installed packages"""
        for col in self.pacman.cols:
            for pac in self.pacman[col]:
                if not pac.get_installed():
                    image = "red"
                    name = pac.get_name()
                    version = pac.get_version()
                    inst_ver = pac.get_inst_ver()
                    col = pac.get_collection()
                    self.append([image, name, version, inst_ver, col])
        return

class combo_model(gtk.ListStore):
    """Sets a model for the combobox"""
    def __init__(self, pacman):
        """Init the model and sets its content"""
        gtk.ListStore.__init__(self, str)

        self.append([_("All")])
        self.append([_("Installed")])
        self.append([_("Not installed")])
        self.append([_("To upgrade")])
        self.append([_("Orphans")])
        for col in pacman.cols:
            if col == "no_col":
                self.append([_("Manually installed")])
            else:
                self.append([col.capitalize()])
        self.append([_("Search for...")])

class dep_model(gtk.ListStore):
    """Sets a model for the dependencies list"""
    def __init__(self, pacman, name, gld):
        """Init the model and sets its content"""
        gtk.ListStore.__init__(self, str, str, str)

        try:
            package = pacman.get_by_name(name)

        except NameError:
            print _("This is probably a bug\n\
            Please, report it at http://gna.org/projects/gtkpacman")
            raise

        if not package.is_setted():
            pacman.set_pac_properties(package)
        
        for name in package.get_dependencies():

            image = ""
            try:
                pac = pacman.get_by_name(name)
            except NameError:
                if name.count(">="):
                    (name, rec_ver) = name.split(">=")
                    try:
                        pac = pacman.get_by_name(name)
                    except NameError:
                        self.append(["blank", name, "NONE"])
                        continue
                    if pac.get_installed():
                        if rec_ver < pac.get_version():
                            image = "yellow"
                        else:
                            image = "green"
                    else:
                        image = "red"

                    coll = pac.get_collection()
                    self.append([image, name, coll])
                    continue
                else:
                    self.append(["blank", name, "NONE"])
                    continue
            
            if pac.get_isold():
                image = "yellow"
            elif pac.get_installed():
                image = "green"
            else:
                image = "red"
                
            name = pac.get_name()
            coll = pac.get_collection()

            self.append([image, name, coll])

class req_by_model(gtk.ListStore):

    def __init__(self, pacman, name):

        gtk.ListStore.__init__(self, str, str, str)
        pac = pacman.get_by_name(name)
        if not pac.is_setted():
            pacman.set_pac_properties(pac)
        req_by_list = pac.get_req_by()
        for pack in req_by_list:
            try:
                pac = pacman.get_by_name(pack)
            except NameError:
                continue
            if pac.get_isold():
                image = "yellow"
            elif pac.get_installed():
                image = "green"
            else:
                image = "red"
            col = pac.get_collection()
            self.append([image, pack, col])

        
