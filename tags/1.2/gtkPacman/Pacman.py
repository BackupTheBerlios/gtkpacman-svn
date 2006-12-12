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

import os, string, re

class package:
    """Class describing a package"""
    def __init__(self,
                 name,
                 version,
                 inst_ver=None,
                 coll=None,
                 inst=True,
                 isold=False):
        """Init a package. Sets foundamental properties"""

        self.name = name
        self.version = version
        self.coll = coll
        self.inst = inst
        if inst_ver:
            self.inst_ver = inst_ver
        elif inst:
            self.inst_ver = version
        else:
            self.inst_ver = "-"
        self.isold = isold
        self.description = ""
        self.filelist = ""
        self.isorphan = True
        self.req_by = ""
        self.prop_setted = False
        
    def get_name(self):
        """Return package's namee"""
        return self.name

    def get_version(self):
        """Return package's version"""
        return self.version

    def get_inst_ver(self):
        """Returned package's installed version"""
        return self.inst_ver

    def get_collection(self):
        """Return the collection where the package is"""
        return self.coll

    def get_installed(self):
        """Returm True if package is installed, False elsewhere"""
        return self.inst

    def get_isold(self):
        """Return True is package is installed but the installed version is
        older than the version in the db, False elsewhere"""
        return self.isold

    def set_version(self, version):
        """Set package's version"""
        if type(version) == type(str):
            self.version = version
        else:
            raise TypeError, _('version must be a string')
        return
    
    def set_isold(self, isold):
        """"""
        if type(isold) == type(True):
            self.isold = isold
        else:
            raise(TypeError, 'inst must be True or False')
        return

    def set_inst_ver(self, inst_ver):
        """"""
        if type(inst_ver) == type(str):
            self.inst_ver = inst_ver
        else:
            raise TypeError, _('inst_ver must be a string')
        return
    
    def set_dependencies(self, deps):
        """Set package's dependencies"""
        self.dependencies = deps
        return
    
    def get_dependencies(self):
        """Return package's dependencies"""
        return self.dependencies

    def set_description(self, desc):
        """Set package's description"""
        self.description = desc
        return

    def get_description(self):
        """Return package's desctription"""
        return self.description

    def set_filelist(self, filelist):
        """Set package's installed files list"""
        self.filelist = filelist
        return
    
    def get_filelist(self):
        """Return package's installed iles list"""
        return self.filelist

    def set_orphan(self, orphan=False):
        """Set the isorphan package's property"""
        self.isorphan = orphan
        return

    def get_orphan(self):
        """Reurn True if the package is orphan, False elsewhere"""
        return self.isorphan

    def set_req_by(self, req_by):
        """Set package's required by list"""
        self.req_by = req_by
        return
    
    def get_req_by(self):
        """Return a list of packages who needs package"""
        return self.req_by

    def setted(self, setted):
        """If properties are setted"""
        self.prop_setted = setted
        return
    
    def is_setted(self):
        """Return True if properties have been setted, False elsewhere"""
        return self.prop_setted
    
class database(dict):
    """The database of gtkPacman, where all pacs are stored and ordered"""
    def __init__(self):
        """Init database"""
        #Get cols present on machine
        self.cols = os.listdir("/var/lib/pacman")

        #Remove some undesiderable voices of cols list
        self.cols.remove("local")
        try:
            self.cols.remove("wget-log")
        except ValueError:
            pass
        self.cols.sort()
        self.set_pacs()
        self.cols.append("no_col")

        #Init some variable which will be usefull
        self.olds = []
        self.orphans = []
        self.set_orphans()
        
    def set_pacs(self):
        """Grab all pacs from machine db, instatiate a package obj for each
        of them and order them by cols"""
        #Grab installed packages
        installed = os.listdir("/var/lib/pacman/local")
        installed.sort()
        inst_pacs = {}
        for pac in installed:
            name_n_ver = pac.split("-", pac.count("-")-1)
            ver = name_n_ver.pop()
            name = ""
            for part in name_n_ver:
                if name:
                    name = "-".join((name, part))
                else:
                    name = part
            #To each name corresponds a version
            inst_pacs[name] = ver
        
        for col in self.cols:
            if col == "testing":
                continue
            self[col] = []
            #Grab all pacs in the col
            try:
                pacs = os.listdir("/var/lib/pacman/%s" %col)
            except OSError:
                self.cols.remove(col)
                continue
            try:
                pacs.remove(".lastupdate")
            except ValueError:
                pass
            pacs.sort()
            for pac in pacs:
                #Take the dir name and split it in name and version
                name_n_ver = pac.split("-", pac.count("-")-1)
                ver = name_n_ver.pop()
                name = ""
                for part in name_n_ver:
                    if name:
                        name = "-".join((name, part))
                    else:
                        name = part
                #If name is in the inst_pacs keys the it's installed...
                if name in inst_pacs.keys():
                    inst = True
                    #..then we can remove it from inst_pacs
                    inst_ver = inst_pacs.pop(name)
                    #...and if its ver is greater then the installed one
                    #is old...
                    if ver > inst_ver:
                        isold = True
                    else:
                        isold = False
                #...else it's not installed
                else:
                    inst = False
                    inst_ver = None
                    isold = None
                #Instantiate a package obj and append it to col's pacs list
                self[col].append(package(name, ver, inst_ver, col, inst,isold))

        self["no_col"] = []
        #Pacs which still are in inst_pacs aren't in the local repo, so they're
        #"manually installed"
        for pac in inst_pacs.keys():
            inst = True
            ver = inst_pacs[pac]
            self["no_col"].append(package(pac, ver, ver, "NONE"))

        #self.set_testing()
        return

    def set_pac_properties(self, pac):
        """Set the properties for the given pac"""
        repo = pac.get_collection()
        name = pac.get_name()
        if pac.get_installed():
            version = pac.get_inst_ver()
            repo = "local"
        else:
            version = pac.get_version()
        pack_dir = "-".join((name, version))
        path = "/var/lib/pacman/%(col)s/%(dir)s" %{
            "col": repo,
            "dir": pack_dir
            }
        self.set_description(pac, path)
        self.set_dependencies(pac)
        self.set_filelist(pac, repo, path)
        self.set_req_by(pac)
        pac.setted(True)
        return

    def set_description(self, pac, path):
        """Set description for the given pac"""
        desc = open("%s/desc" %path)
        description = ""
        for line in desc:
            if re.search("\%DESC\%", line):
                description = desc.next()
        pac.set_description(description)
        return

    def set_dependencies(self, pac):
        """Set dependencies list for the given pac"""
        col = pac.get_collection()
        if col == "NONE":
            col = "local"
        ver = pac.get_version()
        name = pac.get_name()
        directory = "-".join((name, ver))
        deps = open("/var/lib/pacman/%(col)s/%(dir)s/depends" %{
            "col": col,
            "dir": directory}).read()

        dependencies = []
        begin = deps.find("%DEPENDS%") + len("%DEPENDS%")
        if col == "local":
            end = deps.find("%REQUIREDBY%")
        else:
            end = deps.find("%CONFLICTS")
        dependencies = deps[begin:end].strip()
        if dependencies:
            pac.set_dependencies(dependencies.split("\n"))
        else:
            pac.set_dependencies("")
        return
    
    def set_filelist(self, pac, repo, path):
        """Set installed files list for the given pac"""
        if repo == "local":
            files = open("%s/files" %path).read()
            begin = files.find("%FILES%") + len("%FILES%")
            end = files.find("%BACKUP%")
            filelist = files[begin:end].strip()
            pac.set_filelist(filelist)
            
        return

    def set_req_by(self, pac):
        """Set list of packages that needs given pac"""
        if not pac.get_installed():
            return
        
        name = pac.get_name()
        version = pac.get_inst_ver()
        directory = "-".join((name, version))
        path = "/var/lib/pacman/local/%s" %directory
        depends = open("%s/depends" %path).read()

        begin = depends.find("%REQUIREDBY%") + len("%REQUIREDBY%")
        end = depends.find("%CONFLICTS%")

        reqs = depends[begin:end].strip().split("\n")
        if reqs:
            pac.set_req_by(reqs)
        else:
            pac.set_req_by("")
        return
    
    def set_orphans(self):
        """Set orphans pacs"""
        self.orphans = []
        for col in self.cols:
            try:
                self[col]
            except KeyError:
                self.cols.remove(col)
                continue
            for pac in self[col]:
                if not pac.get_installed():
                    continue
                name = pac.get_name()
                version = pac.get_inst_ver()
                repo = "local"
                
                pack_dir = "-".join((name, version))
                path = "/var/lib/pacman/%(col)s/%(dir)s" %{
                    "col": repo,
                    "dir": pack_dir
                    }
                desc = open("%s/desc" %path).read()

                reason = 0
                begin = desc.find("%REASON%")

                if begin == -1:
                    continue
                
                begin += len("%REASON%")
                reason = desc[begin:].strip()
                if bool(int(reason)):
                    pac.set_orphan(False)
                else:
                    pac.set_orphan(True)
                    self.orphans.append(pac)
                
    def get_by_name(self, name):
        """Return the pckage named 'name', or raise a NameError"""
        for col in self.cols:
            for pac in self[col]:
                if name == pac.get_name():
                    return pac
        raise NameError, "%s is not in the database" %name
    
    def set_olds(self):
        """Set old pacs"""
        for col in self.cols:
            if col == "no_col":
                continue
            for pac in self[col]:
                if pac.get_isold():
                    self.olds.append(pac)
                continue
            continue
        return

    def get_olds(self):
        """Return old pacs"""
        return self.olds
    
    def get_by_desc(self, desc):
        """Return pacs which description match with desc"""
        pacs = []
        for col in self.cols:
            for pac in self[col]:
                description = pac.get_description()
                if description.count(desc):
                    pacs.append(pac)

        return pacs
    
    def get_by_keywords(self, keywords):
        """Return pacs which have keywords as name or in description"""
        #Split keywords by '+' or spaces
        if keywords.count("+"):
            keys = keywords.split("+")
        elif keywords.count(" "):
            keys = keywords.split()
        else:
            keys = keywords

        pacs = []
        #Then using get_by_desc and get_by_name get the packages
        if type(keys) == type(list()):
            for key in keys:
                try:
                    pac = self.get_by_name(key)
                except NameError:
                    pac = None
                if pac:
                    pacs.append(pac)
                pac = self.get_by_desc(key)
                if pac:
                    if not pacs.count(pac):
                        pacs.append(pac)
        else:
            try:
                pac = self.get_by_name(keys)
            except NameError:
                pac = None
            if pac:
                pacs.append(pac)
            pac = self.get_by_desc(keys)
            if pac:
                if not pacs.count(pac):
                    pacs.append(pac)
        return pacs

    def get_orphans(self):
        """Return orphan pacs"""
        return self.orphans
    def refresh(self):
        """Refresh the database"""
        self.__init__()
