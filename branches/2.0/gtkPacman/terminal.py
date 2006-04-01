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

from gtk import threads_leave, threads_enter
from vte import Terminal

class terminal(Terminal):

    def __init__(self, error_cbk, success_cbk):

        Terminal.__init__(self)

        self.error_cbk = error_cbk
        self.success_cbk = success_cbk
        self.last = ""
        self.id = None
        
    def install(self, pac, row):
        threads_enter()
        command = "pacman"
        argv = ("pacman", "-Sd", "--noconfirm", pac.name)
        self.last = pac

        if self.id:
            self.disconnect(self.id)
            
        self.id = self.connect("child-exited", self.quit, self.error_cbk,
                               self.success_cbk, row, "install")

        self.fork_command(command, argv)
        #self.feed_child("pacman -Sd --noconfirm %s;exit\n" %pac.name)
        threads_leave()

    def remove(self, pac, row, force):
        threads_enter()
        command = "pacman"

        if not force:
            argv = ("pacman", "-Rd", "--noconfirm", pac.name)
        else:
            argv = ("pacman", "-Rdf", "--noconfirm", pac.name)
                   
        self.last = pac

        if self.id:
            self.disconnect(self.id)
            
        self.id = self.connect("child-exited", self.quit, self.error_cbk,
                               self.success_cbk, row, "remove")
        
        self.fork_command(command, argv)
        #self.feed_child("%s;exit\n" %command)
        threads_leave()

    def quit(self, term, error_cbk, success_cbk, row, what):
        from gtk import STOCK_APPLY, STOCK_CANCEL
        
        text = self.get_text(lambda terminal,col,row,data: True)

        if "error" in text:
            error_cbk(row, self.last, what)
            row[0] = STOCK_CANCEL
        else:
            success_cbk(row)
            row[0] = STOCK_CANCEL
        return
            
