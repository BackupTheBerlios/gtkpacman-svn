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
# gtkPacman is copyright (C)2005-2008 by Stefano Esposito

from vte import Terminal

class terminal(Terminal):

    def __init__(self):

        Terminal.__init__(self)
        self.fork_command()
        self.set_sensitive(False)
    
    def _constructCmds(self, queues):
        inst = ''
        inst_dep = ''
        rm = ''
        
        for pac in queues["add"]:
            # Package should be installed as dependancy if flag == 11. 
            # Add it inst_dep
            if pac.flag == 11:
                inst_dep = inst_dep + ' ' + pac.name
            # Otherwise add it to inst
            else:
                inst = inst + ' ' +pac.name
        
        for pac in queues["remove"]:
            rm = rm + ' ' + pac.name
        
        return inst, inst_dep, rm
        
    def do(self, queues):
        inst, inst_dep, rm = self._constructCmds(queues)
        pacman = "pacman --noconfirm"
        commands = []
            
        if inst:
            cmd_inst = "%s -Sdf %s \n" %(pacman, inst)
            commands.append(cmd_inst)            
        if inst_dep:
            cmd_inst_dep = "%s -Sdf --asdep %s \n" %(pacman, inst_dep)
            commands.append(cmd_inst_dep)
        if rm:
            cmd_rem = "%s -Rdf %s \n" %(pacman, rm)
            commands.append(cmd_rem)
            
        commands.append("exit \n")                
        map(self.execute, commands)
        
    def do_local(self, fname, queues):
        inst, inst_dep, rm = self._constructCmds(queues)
        pacman = "pacman --noconfirm" 
        local = "%s -Uf %s" %(pacman, fname)
        commands = []
        
        if inst:
            cmd_inst = "%s -Sdf %s \n" %(pacman, inst)
            commands.append(cmd_inst)
        if inst_dep:
            cmd_inst_dep = "%s -Sdf --asdep %s \n" %(pacman, inst_dep)
            commands.append(cmd_inst_dep)
        if rm:
            cmd_rem = "%s -Rdf %s \n" %(pacman, rm)
            commands.append(cmd_rem)
        
        cmd_inst_file = "%s \n" %local
        commands.append(cmd_inst_file)
        commands.append("exit \n")
        map(self.execute, commands)

    def do_upgrade(self):
        self.execute("pacman -Su --noconfirm;exit\n")

    def execute(self, cmd):
        # Insert commands to terminal
        self.feed_child(cmd)

    def close(self, term, close_button):
        close_button.show()
        return
