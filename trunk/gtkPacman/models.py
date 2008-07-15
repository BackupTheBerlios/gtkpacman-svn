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
#***********************************
class orphan_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str)

        for pac in pacs:
            if pac.isold:
                image = "yellow"
                inst_ver = pac.inst_ver
            else:
                image = "green"
                inst_ver = pac.inst_ver

            self.append([image, None, pac.name, inst_ver, pac.version])
#*********************************
class whole_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, str)
        
        for r_list in pacs:
            for pac in r_list:
		# We don't want to add pacs from local repo or we will have duplicates
		if pac.repo == 'local':
		    continue
		    
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
	