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
#
# This file is freely inspired to chapter 13.5 of "Python tips and tricks", by
# the italianpug(http://www.italianpug.org). The code in that chapter is by
# Luigi Pantano aka bornfreethinker.

from ConfigParser import *

class configuration(SafeConfigParser):
    """Define the class used to manage configuration file"""
    def __init__(self, cfg, areroot):
        """Init the config object"""
        SafeConfigParser.__init__(self)

        if areroot:
            self.cfg = file(cfg, "r+")
        else:
            self.cfg = file(cfg)
        
    def get_value(self, key, section=None, g_type="bool"):
        """Get give option's value. If a section is specified search only
        in that section"""
        if not section:
            for sect in self.sections():
                if self.has_option(sect, key):
                    if g_type == "string":
                        return self.get(sect, key)
                    if g_type == "int" :
                        return self.getint(sect, key)
                    if g_type == "bool" :
                        return self.getboolean(sect, key)
        else:
            if self.has_option(section, key):
                if g_type == "string":
                    return self.get(section, key)
                if g_type == "int" :
                    return self.getint(section, key)
                if g_type == "bool" :
                    return self.getboolean(section, key)
                
    def set_option(self, pair, value):
        """Set a value for the given option"""
        section = pair["section"]
        key = pair["option"]
        try:
            self.set(section,key,value)
        except NoSectionError:
            try:
                self.add_section(section)
            except DuplicateSectionError:
                return 0

            self.set(section,key,value)

    def get_common_pref(self, get_refresh=False):
        """Get the common section options and values"""
        args = ""
        if self.get_value("use_alt_root", "common"):
            alt_root = self.get_value("alt_root", "common", "string")
            args = " ".join((args, "-r", alt_root))

        if self.get_value("use_alt_db", "common"):
            alt_db = self.get_value("alt_db", "common", "string")
            args = " ".join((args, "-b", alt_db))

        if self.get_value("use_alt_conf", "common"):
            alt_conf = self.get_value("alt_conf", "common", "string")
            args = " ".join((args, "--config", alt_conf))

        if get_refresh:
            if self.get_value("refresh", "common"):
                args = " ".join((args, "-y"))

        if self.get_value("verbose", "common"):
            args = " ".join((args, "-v"))

        return args

    def get_x_pref(self, section):
        """Get the options a values for add, up or sync section"""
        args = ""
        if self.get_value("noconfirm", section):
            args = " ".join((args, "--noconfirm"))

        if self.get_value("force", section):
            args = " ".join((args, "-f"))

        if not self.get_value("dep_check", section):
            args = " ".join((args, "-d"))

        if section == "sync":
            if self.get_value("down_only", section):
                args = " ".join((args, "-w"))

        return args

    def get_remove_pref(self):
        """Get options values for the remove section"""
        args = ""
        if self.get_value("recursive", "remove"):
            args = " ".join((args, "-s"))

        if self.get_value("cascade", "remove"):
            args = " ".join((args, "-c"))

        if not self.get_value("dep_check", "remove"):
            args = " ".join((args, "-d"))

        if self.get_value("nosave", "remove"):
            args = " ".join((args, "-n"))

        if self.get_value("db_only", "remove"):
            args = " ".join((args, "-k"))

        return args

    def get_refresh(self):
        """Get refresh option"""
        if self.get_value("refresh", "common"):
            return "-y"
        else:
            return " "
