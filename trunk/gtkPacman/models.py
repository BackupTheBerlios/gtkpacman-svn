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

from gtk import ListStore, TreeStore, TreeView
from gtk import CellRendererPixbuf, CellRendererText, TreeViewColumn

class installed_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, int)
        
        for pac_tuple in enumerate( pacs ):
            if not pac_tuple[1].installed:
                continue
            
            position = pac_tuple[0]
            if pac_tuple[1].isold:
                image = "yellow"
            else:
                image = "green"
                
            self.append([image, None, pac_tuple[1].name, pac_tuple[1].inst_ver, pac_tuple[1].version, position])

class all_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, int)

        for pac_tuple in enumerate( pacs ):         
            position = pac_tuple[0]
            
            if not (pac_tuple[1].isold or pac_tuple[1].installed):
                image = "red"
                inst_ver = "-"
            elif pac_tuple[1].isold:
                image = "yellow"
                inst_ver = pac_tuple[1].inst_ver
            else:
                image = "green"
                inst_ver = pac_tuple[1].inst_ver

            self.append([image, None, pac_tuple[1].name, inst_ver, pac_tuple[1].version, position])
            continue
#***********************************
class orphan_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, int)

        for pac_tuple in enumerate( pacs ):
            position = pac_tuple[0]
            
            if not pac_tuple[1].isorphan:
                continue
            if pac_tuple[1].isold:
                image = "yellow"
                inst_ver = pac_tuple[1].inst_ver
            else:
                image = "green"
                inst_ver = pac_tuple[1].inst_ver

            self.append([image, None, pac_tuple[1].name, inst_ver, pac_tuple[1].version, position])
#*********************************
class explicitly_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, int)
        

        for pac_tuple in enumerate(pacs):
            position = pac_tuple[0]
                
            if pac_tuple[1].explicitly[1] and pac_tuple[1].isold:
                image = "yellow"
                inst_ver = pac_tuple[1].inst_ver
            elif pac_tuple[1].explicitly[1] and not pac_tuple[1].isold:
                image = "green"
                inst_ver = pac_tuple[1].inst_ver
            else:
                continue

            self.append([image, None, pac_tuple[1].name, inst_ver, pac_tuple[1].version, position])

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

class file_list(TreeStore):

    def __init__(self, files):

        TreeStore.__init__(self, str)

        splitted = []
        for line in files.splitlines():
            part = line.split("/")
            try:
                part.remove('')
            except ValueError:
                pass
            splitted.append(part)
            continue

        nodes={}
        for split in splitted:
            last = None
            for part in split:
                if part in nodes.keys():
                    if split.index(part) == len(split)-1:
                        continue
                    last = part
                continue

            if not last:
                nodes[split[0]] = self.append(None, [split[0]])
            else:                
                idx = split.index(last)+1
                nodes[split[idx]] = self.append(nodes[last], [split[idx]])
            continue
        
class PacViewModel( ListStore):
    def __init__(self, queue):
        ListStore.__init__(self, str, str, str)
        
        for pac in queue:
            version = pac.inst_ver
            if pac.isold:
                image = "yellow"
            elif pac.installed:
                image = "green"
            else:
                image = "red"
                version = pac.version

            self.append([image, pac.name, version])
        
class PacView( TreeView):
    def __init__(self, queue):
        TreeView.__init__( self, PacViewModel(queue))
        self.set_property( "enable-search", False)
        self.set_headers_clickable(True)
        
        pix = CellRendererPixbuf()
        column = TreeViewColumn( '', pix, stock_id=0)
        self.append_column( column)
        
        cell = CellRendererText()
        column = TreeViewColumn( 'Package', cell, text=1)
        self.append_column( column)
        
        cell = CellRendererText()
        column = TreeViewColumn( 'Version', cell, text=2)
        self.append_column( column)
        