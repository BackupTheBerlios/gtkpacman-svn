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

import os, string, re

class package:
    """Class describing a package"""
    def __init__(self,
                 name,
                 version,
                 inst_ver=None,
                 repo=None,
                 inst=True,
                 isold=False):
        """Init a package. Sets foundamental properties"""

        self.name = name
        self.version = version
        self.repo = repo
        self.installed = inst
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
        self.dependencies = ""
        self.prop_setted = False
        
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
            raise TypeError, _('inst must be True or False')
        return

    def set_inst_ver(self, inst_ver):
        """"""
        if type(inst_ver) == type(str):
            self.inst_ver = inst_ver
        else:
            raise TypeError, _('inst_ver must be a string')
        return

    def download(self, server_dict, callback_func=None):
        #This function is taken and adapted from libpypac.
        #libpypac is Copyright (C) 2005 Libpypac Foundation
        #libpypac is released under LGPL
        #This function is released under the same license of gtkpacman

        import ftplib, httplib
        
        pac_name = "-".join((self.name, self.version))
        for server in server_dict[self.repo]:
            s_list = server.rsplit("//")
            str = s_list[-1]
            s_list = str.rsplit("/")
            host = s_list[0]

            s_list = s_list[1:]
            cwd = ""
      
            for i in range(len(s_list)):
                cwd = "/%s%s" %(s_list.pop(), cwd)

            path = "/var/cache/pacman/pkg/%s.pkg.tar.gz.part" %pac_name
            final_fname = "/var/cache/pacman/pkg/%s.pkg.tar.gz" %pac_name
                
            if server.startswith("ftp"):
                try:
                    ftp_class = ftplib.FTP(host)
                    ftp_class.login("anonymous")
                    ftp_class.cwd(cwd)
                    ftp_class.voidcmd("TYPE I")
                    
                    if os.path.exists(path):
                        transfered = os.path.getsize(path)
                        ftp_class.sendcmd("REST %s" %transfered)
                        loc_file = open(path, "ab")
                    else:
                        transfered = 0
                        loc_file = open(path, "wb")
          
                    socket, totsize = ftp_class.ntransfercmd("RETR %s.tar.gz" %pac_name, transfered)
                    
                    while True:
                        buf = socket.recv(8192)
                        if not len(buf):
                            break
                        loc_file.write(buf)
                        transfered += len(buf)
                        if callback_func != None:
                            callback_func(pac_name, transfered, self.size)
          
                    ftp_class.close()
                    loc_file.close()
                    os.rename(path, final_fname)
                    return "1"
        
                except:
                    try:
                        loc_file.close()
                    except:
                        pass
      
            elif server.startswith("http"):
                try:
                    http_class = httplib.HTTPConnection(host)
                    http_class.request("GET", "%s/%s.tar.gz" %(cwd, pac_name))
                    _file = http_class.getresponse()
                    loc_file = open(path, 'wb')
                    transfered = 0
         
                    while True:
                        data = _file.read(8192)
                        if not data: 
                            break
                        loc_file.write(data)
                        transfered += len(data)
                        if callback_func != None:
                            callback_func(pac_name, transfered, size)
          
                    loc_file.close()
                    http_class.close()
                    os.rename(path, final_fname)
                    return "1"
                                                                                                    
                except:
                    try:
                        loc_file.close()
                    except:
                        pass
            
                    return None
            continue
        return
    
class database(dict):
    """The database of gtkPacman, where all pacs are stored and ordered"""
    def __init__(self):
        """Init database"""
        #Get repos present on machine
        self.repos = os.listdir("/var/lib/pacman")

        #Remove some undesiderable voices of repos list
        self.repos.remove("local")
        try:
            self.repos.remove("wget-log")
        except ValueError:
            pass
        self.repos.sort()
        self.set_pacs()
        self.repos.append("foreigners")

        #Init some variable which will be usefull
        self.olds = []
        self.orphans = []
        
    def _get_installed(self):
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
        return inst_pacs

    def _get_repo_pacs(self, repo):
        self[repo] = []
        pacs = None
        #Grab all pacs in the col
        try:
            pacs = os.listdir("/var/lib/pacman/%s" %repo)
        except OSError:
            self.repos.remove(repo)
            return
        try:
            pacs.remove(".lastupdate")
        except ValueError:
            pass
        pacs.sort()
        return pacs

    def _make_pac(self, pac, repo):
        #Take the dir name and split it in name and version
        name_n_ver = pac.split("-", pac.count("-")-1)
        ver = name_n_ver.pop()
        name = "-".join(name_n_ver)
        
        #If name is in the inst_pacs keys the package is installed...
        if name in self.inst_pacs.keys():
            inst = True
            #..then we can remove it from inst_pacs
            inst_ver = self.inst_pacs.pop(name)
            #...and if its ver is greater then the installed one
            #it's old...
            if ver > inst_ver:
                isold = True
            else:
                isold = False
            #...else it's not installed
        else:
            inst = False
            inst_ver = None
            isold = None
        pac_obj = package(name, ver, inst_ver, repo, inst, isold)
        return pac_obj
                    
    def set_pacs(self):
        """Grab all pacs from machine db, instatiate a package obj for each
        of them and order them by cols"""
        self.inst_pacs = self._get_installed()
        
        for repo in self.repos:
            self[repo] = []
            pacs = self._get_repo_pacs(repo)
            if not pacs:
                return
            
            for pac in pacs:
                pac_obj = self._make_pac(pac, repo)
                self[repo].append(pac_obj)
                continue
            continue
        
        self["foreigners"] = []
        #Pacs which still are in inst_pacs aren't in the local repo, so they're
        #"foreigners"
        for pac in self.inst_pacs.keys():
            inst = True
            ver = self.inst_pacs[pac]
            self["foreigners"].append(package(pac, ver, ver, "foreigners"))
        return

    def set_pac_properties(self, pac):
        """Set the properties for the given pac"""
        if pac.installed:
            version = pac.inst_ver
            repo = "local"
        else:
            version = pac.version
            repo = pac.repo
            
        pack_dir = "-".join((pac.name, version))
        path = "/var/lib/pacman/%s/%s" %(repo, pack_dir)
        self._set_summary(pac, path)
        self._set_filelist(pac, path)
        pac.prop_setted = True
        return

    def _set_summary(self, pac, path):
        desc_file = open("%s/desc" %path).read()
        
        desc = self._get_description(desc_file)
        deps = self._get_dependencies(path)
        size = self._get_size(desc_file)

        if pac.installed:
            req_by = self._get_req_by(path)
            packager = self._get_packager(desc_file)
            builddate = self._get_builddate(desc_file)
            installdate = self._get_installdate(desc_file)
            reason = self._get_reason(desc_file)

            summary = _("Description: %s\nDepends on: %s\nRequired by: %s\nSize: %s\nPackager: %s\nBuilt: %s\nInstalled: %s\nReason: %s") %(desc, deps, req_by, size, packager, builddate, installdate, reason)
            pac.req_by = req_by

        else:
            summary = _("Description: %s\nDepends on: %s\nSize (compressed): %s") %(desc, deps, size)

        pac.summary = summary
        pac.dependencies = deps

    def _get_size(self, desc):

        try:
            begin = desc.index("%CSIZE%") + len("%CSIZE%")
        except ValueError:
            begin = desc.index("%SIZE%") + len("%SIZE%")

        end = desc.index("%", begin)
        size_s = desc[begin:end].strip()
        size_int = int(size_s)
        measure = "byte(s)"

        if size_int >= 1024 and size_int < 1048576:
            size_int = size_int/1024
            measure = "kB"
        if size_int >= 1048576:
            size_int = size_int/1048576
            measure = "MB"

        size = "%s %s" %(size_int, measure)
        return size

    def _get_packager(self, desc):
        begin = desc.index("%PACKAGER%") + len("%PACKAGER%")
        end = desc.index("%", begin)

        packager = desc[begin:end].strip()
        return packager

    def _get_builddate(self, desc):
        begin = desc.index("%BUILDDATE%") + len("%BUILDDATE%")
        end = desc.index("%", begin)

        builddate = desc[begin:end].strip()
        return builddate

    def _get_installdate(self, desc):
        begin = desc.index("%INSTALLDATE%") + len("%INSTALLDATE%")
        end = desc.index("%", begin)

        installdate = desc[begin:end].strip()
        return installdate

    def _get_reason(self, desc):
        begin = desc.index("%REASON%") + len("%REASON%")
        reason_int = int(desc[begin:].strip())

        if reason_int:
            reason = _("Installed as a dependency for another package")
        else:
            reason = _("Excplicitly installed")

        return reason
        
    def _get_description(self, desc):
        """Set description for the given pac"""
        begin = desc.index("%DESC%") + len("%DESC%")
        end = desc.index("%", begin)
        description = desc[begin:end].strip()
        return description

    def _get_dependencies(self, path):
        """Set dependencies list for the given pac"""
        deps = open("%s/depends" %path).read()

        dependencies = []
        try:
            begin = deps.index("%DEPENDS%") + len("%DEPENDS%")
        except ValueError:
            return ""
        end = deps.find("%", begin) - len("%")
        dependencies = deps[begin:end].strip()
        depends = dependencies.split("\n")
        deps = ", ".join(depends)
        return deps
    
    def _get_req_by(self, path):
        """Set list of packages that needs given pac"""
        depends = open("%s/depends" %path).read()

        begin = depends.find("%REQUIREDBY%") + len("%REQUIREDBY%")
        end = depends.find("%", begin) - len("%")

        reqs = depends[begin:end].strip().split("\n")
        req_by = ", ".join(reqs)
        return req_by

    def _set_filelist(self, pac, path):
        """Set installed files list for the given pac"""
        if not pac.installed:
            return _("%s is not installed") %pac.name
        
        files = open("%s/files" %path).read()
        begin = files.index("%FILES%") + len("%FILES%")
        end = files.find("%", begin) - len("%")
        filelist = files[begin:end].strip()
        pac.filelist = filelist
        return
    
    def set_orphans(self):
        """Set orphans pacs"""
        self.orphans = []
        for repo in self.repos:
            try:
                self[repo]
            except KeyError:
                self.repos.remove(repo)
                continue
            for pac in self[repo]:
                if not pac.installed:
                    continue
                name = pac.name
                version = pac.inst_ver
                repo = "local"
                
                pack_dir = "-".join((name, version))
                path = "/var/lib/pacman/%s/%s" %(repo, pack_dir)
                desc = open("%s/desc" %path).read()

                reason = 0
                begin = desc.find("%REASON%")

                if begin == -1:
                    continue
                
                begin += len("%REASON%")
                reason = desc[begin:].strip()
                return
                
    def get_by_name(self, name):
        """Return the pckage named 'name', or raise a NameError"""
        for repo in self.repos:
            for pac in self[repo]:
                if name == pac.name:
                    return pac
        raise NameError, _("%s is not in the database") %name
    
    def set_olds(self):
        """Set old pacs"""
        for repo in self.repos:
            if repo == "no_col":
                continue
            for pac in self[repo]:
                if pac.isold:
                    self.olds.append(pac)
                continue
            continue
        return
    
    def get_by_desc(self, desc):
        """Return pacs which description match with desc"""
        pacs = []
        for repo in self.repos:
            for pac in self[repo]:
                if not pac.prop_setted:
                    self.set_pac_properties(pac)
                if pac.description.count(desc):
                    pacs.append(pac)
                continue
            continue
        return pacs
    
    def get_by_keywords(self, keywords):
        """Return pacs which have keywords as name or in description"""
        keys = []
        #Split keywords by '+' or spaces
        if keywords.count("+") and keywords.count(" "):
            keys_1 = keywords.split("+")
            for key in keys_1:
                keys = key.split(" ")
        elif keywords.count(" "):
            keys = keywords.split()
        elif keyword.count("+"):
            keys = keyword.split("+")
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
                if pac and (not pacs.count(pac)):
                    pacs.append(pac)
        else:
            try:
                pac = self.get_by_name(keys)
            except NameError:
                pac = None
            if pac:
                pacs.append(pac)
            pac = self.get_by_desc(keys)
            if pac and (not pacs.count(pac)):
                pacs.append(pac)
        return pacs
    
    def refresh(self):
        """Refresh the database"""
        self.__init__()
