# This file is part of gtkPacman.
#
# gtkPacman is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# gtkPacman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gtkPacman; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# gtkPacman is copyright (C)2005 by Stefano Esposito

from vte import Terminal

class terminal(Terminal):

    def __init__(self, close_button):

        Terminal.__init__(self)

        self.connect("child-exited", self.close, close_button)

    def do(self, queues):
        names_queues = { "add": [], "remove": [] }

        for pac in queues["add"]:
            names_queues["add"].append(pac.name)
            continue
        for pac in queues["remove"]:
            names_queues["remove"].append(pac.name)

        inst_pacs = " ".join(names_queues["add"])
        rem_pacs = " ".join(names_queues["remove"])

        if inst_pacs and rem_pacs:
            command = "pacman -Sdf %s;pacman -Rdf %s;exit\n" %(inst_pacs, rem_pacs)
        elif inst_pacs:
            command = "pacman -Sdf %s;exit\n" %inst_pacs
        elif rem_pacs:
            command = "pacman -Rdf %s;exit\n" %rem_pacs
        else:
            command = "exit\n"
            
        self.fork_command()
        self.feed_child(command)

    def close(self, term, close_button):

        close_button.show()
        return
