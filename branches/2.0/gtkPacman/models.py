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

from gtk import ListStore

class installed_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str)

        for pac in pacs:
            if not pac.installed:
                continue

            if pac.isold:
                image = "yellow"
            else:
                image = "green"
                
            self.append([image, None, pac.name, pac.inst_ver, pac.version])
            continue

class all_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str)

        for pac in pacs:
            if not (pac.isold or pac.installed):
                image = "red"
                inst_ver = "-"
            elif pac.isold:
                image = "yellow"
                inst_ver = pac.inst_ver
            else:
                image = "green"
                inst_ver = pac.inst_ver

            self.append([image, None, pac.name, inst_ver, pac.version])
            continue

class whole_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, str)
        
        for r_list in pacs:
            for pac in r_list:
                if not (pac.isold or pac.installed):
                    image = "red"
                    inst_ver = "-"
                elif pac.isold:
                    image = "yellow"
                    inst_ver = pac.inst_ver
                else:
                    image = "green"
                    inst_ver = pac.inst_ver

                self.append([image, None, pac.name, inst_ver, pac.version, pac.repo])

class search_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, str)

        for pac in pacs:
                
            if not (pac.isold or pac.installed):
                image = "red"
                inst_ver = "-"
            elif pac.isold:
                image = "yellow"
                inst_ver = pac.inst_ver
            else:
                image = "green"
                inst_ver = pac.inst_ver

            self.append([image, None, pac.name, inst_ver, pac.version, pac.repo])
