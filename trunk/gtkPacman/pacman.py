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

import os, re, time
#from time import ctime

path_repo = str()
path_local = "/var/lib/pacman/local"

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
        # [0] = Package description, [1] = Packager
        self.description = [None, None]
        self.filelist = ""
        self.isorphan = None
        self.req_by = ""
        self.dependencies = ""
        self.prop_setted = False
        # [0] = Install date, [1] = Build date
        self.dates = [None, None]
        # Explicitly will be used for showing packages that ware installed explicitly
        self.explicitly = ["", None]
        # Flag is for marking package as " install as dependency ", ( flag = 11 )
        self.flag = None
        self.size = ""
        
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
    
class database(dict):
    """The database of gtkPacman, where all pacs are stored and ordered"""
    def __init__(self):
        """Init database"""
        #Get repos present on machine
        self.ignorePkg = []
        self.holdPkg = []
        # {log path:log}
        self.log = {}
        
        self._get_pacman_version()
        self.repos = self._get_repos()
        self._get_log()

        self.set_pacs()
        self.repos["foreigners"] = None

        #Init some variable which will be usefull
        self.olds = []
        self.orphans = []

    def _get_repos(self):
        conf_file = file("/etc/pacman.conf", "r").read()
        conf_file_lines = conf_file.splitlines()
 
        repos = {}
        for line in conf_file_lines:
            if line.startswith("#"):
                continue

            if line.startswith("["):
                begin = line.index("[") + len("[")
                end = line.index("]")
                repo = line[begin:end].strip()
                if repo == "options":
                    continue
                else:
                    repos[repo] = None
                continue

            if line.startswith( 'LogFile' ):
                l = line.split( '=' )[1:]
                self.log[ l[0].strip() ] = None
            if line.startswith("IgnorePkg"):
                begin = line.index("=")+1
                pkgs = line[begin:].split(" ")
                self.ignorePkg.extend(pkgs)
                continue
            if line.startswith("HoldPkg"):
                begin = line.index("=")+1
                pkgs = line[begin:].split(" ")
                self.holdPkg.extend(pkgs)
                continue
            continue
        return repos
        
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

    def _get_pacman_version (self):
        [stin, stout] = os.popen2("pacman --version|grep Pacman")
        self.ver = stout.read().split('v')[1].split('-')[0].strip().split('.')
        
    def _get_log(self):
        log_path = self.log.keys()[0]
        
        try:
            log_file = open(log_path, 'r')
        except IOError:
            return

        log = log_file.readlines()
        log_file.close()
        
        self.log[log_path] = log
        
    def _get_repo_pacs(self, repo):
        global path_repo
        pacs = None
        #Grab all pacs in the col
        if (self.ver[0] >= '3' and self.ver[1] >= '1'):
            path_repo = path = "/var/lib/pacman/sync"
        else:
            path_repo = path = "/var/lib/pacman"
        
        try:
            pacs = os.listdir("%s/%s" %(path, repo))
        except OSError:
            self.repos.pop(repo)
            return
        try:
            pacs.remove(".lastupdate")
        except ValueError:
            pass

        date_file = open("%s/%s/.lastupdate" %(path, repo), 'r')
        date = int( date_file.readline() )
        date_file.close()
        
        self.repos[repo] = time.ctime(date)

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
            
            # comparison is done by comparing two strings,
            # so when cmp for example '2.8' and '2.10' then
            # '2.8' will be greater than '2.10', this is why we cmp
            # versions length as well, to get more accurate result
            if ver == inst_ver:
                isold = False
            elif ver > inst_ver or len(ver) > len(inst_ver):
                isold = True
            else:
                print """?? can't figure out status of this package:
                package: %s
                installed ver. %s - avaible ver. %s
                Marked package as 'old'""" %(name, inst_ver, ver)
                isold = True
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
        self["local"] = []
        self.inst_pacs = self._get_installed()
        
        for repo in sorted(self.repos.keys()):
            self[repo] = []
            pacs = self._get_repo_pacs(repo)
            if not pacs:
                continue
            
            for pac in pacs:
                pac_obj = self._make_pac(pac, repo)
                if pac_obj.installed:
                    self[repo].append(pac_obj)
                    ver = pac_obj.inst_ver
                    pac_local = package( pac_obj.name, pac_obj.version, pac_obj.inst_ver, pac_obj.repo, pac_obj.installed, pac_obj.isold )
                    self["local"].append(pac_local)
                else:
                    self[repo].append(pac_obj)
        
        self["foreigners"] = []
        #Pacs which still are in inst_pacs aren't in the local repo, so they're
        #"foreigners"
        for pac in self.inst_pacs.keys():
            inst = True
            ver = self.inst_pacs[pac]
            pac_local = package(pac, ver, ver, "foreigners")
            self["foreigners"].append(pac_local)
            self['local'].append(pac_local)
        return
    
    def set_pac_properties(self, pac):
        """Set the properties for the given pac"""
        if pac.installed:
            raw_desc = self._get_raw_desc(pac, "desc")
            raw_depends = self._get_raw_desc(pac, "depends")
            raw_files = self._get_raw_desc(pac, "files")
            
            pac.description = [ self._get_description(raw_desc), self._get_packager(raw_desc) ]
            pac.dates = [ self._get_installdate(raw_desc), self._get_builddate(raw_desc) ]
            pac.explicitly = self._get_reason(raw_desc)
            pac.size = self._get_size(raw_desc)
            
            pac.dependencies, pac.req_by = self._search_dependencies(pac)
            self._set_filelist(pac, raw_files)
            
        else:
            raw_desc = self._get_raw_desc(pac, "desc")
            raw_depends = self._get_raw_desc(pac, "depends")
            
            pac.description = [ self._get_description(raw_desc), self._get_packager ]
            pac.dependencies = self._get_dependencies(raw_depends)
            pac.size = self._get_size(raw_desc)
        
        pac.prop_setted = True
        
    def _search_dependencies(self, pac):
        # Search in local repo for pac_name in descriptions files.
        # If found than pack.name is requied by pack_name
        deps_stack = []
        deps_on = ''
        deps = ''
        
        req_stack = []
        req_by = ''
        req = ''
        
        # Get dependencies only from "pac"
        pac_raw_req_by = self._get_raw_desc(pac, "depends")
        pac_req_by = self._get_dependencies(pac_raw_req_by)
        
        for p in pac_req_by.split(','):
            if '=<' in p:
                p = p.split('=<')[0]
            if '>=' in p:
                p = p.split('>=')[0]
            p = p.strip()
            deps_stack.append(p)
        
        for package in self["local"]:
            
            if not package.prop_setted:
                # Get Required package
                raw_depends = self._get_raw_desc(package, "depends")
                depends_on = self._get_dependencies(raw_depends)
                for p in depends_on.split(','):
                    p = p.strip()
                    if '=<' in p:
                        p = p.split('=<')[0]
                    if '>=' in p:
                        p = p.split('>=')[0]
                    if (p == pac.name and (package.name not in req_stack and package.name != pac.name)):
                        req_stack.append(package.name)
                
                # Get dependencies
                req_by = self._get_req_by(raw_depends)
                for p in req_by.split(','):
                    p = p.strip()
                    if '=<' in p:
                        p = p.split('=<')[0]
                    if '>=' in p:
                        p = p.split('>=')[0]
                    if p == pac.name and package.name not in deps_stack and package.name != pac.name:
                        deps_stack.append(package.name)
            else:
                continue
    
        for dep_name in deps_stack:
            deps = deps + ", " + dep_name
        deps = deps[2:]
        
        for req_name in req_stack:
            req = req + ", " + req_name
        req = req[2:]
        
        return deps, req
        
    def _get_raw_desc(self, pac, desc_f):
        global path_repo
        repo = pac.repo
        if pac.installed:
            name_n_ver = pac.name + '-' + pac.inst_ver
            path = '/var/lib/pacman/local/%s/%s' %(name_n_ver, desc_f)
        else:
            name_n_ver = pac.name + '-' + pac.version
            path = "%s/%s/%s/%s" %(path_repo, repo, name_n_ver, desc_f)

        try:
            raw_file = open(path).read()
        except IOError, msg:
            print "!! Warning: can't open %s \n\t" %path, msg
            return None
            
        return raw_file

    def _get_size(self, desc):

        try:
            begin = desc.index("%CSIZE%") + len("%CSIZE%")
        except (AttributeError, IndexError, ValueError):
            try:
                begin = desc.index("%SIZE%") + len("%SIZE%")
            except (AttributeError, IndexError, ValueError):
                return "Not Found"

        try:
                end = desc.index("%", begin)
                size_s = desc[begin:end].strip()
        except ValueError:
                size_s = desc[begin:].strip()
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
        try:
            begin = desc.index("%PACKAGER%") + len("%PACKAGER%")
            end = desc.index("%", begin)
        except (AttributeError, IndexError):
            return "Not Found"

        packager = desc[begin:end].strip()
        return packager

    def _get_builddate(self, desc):
        try:
            begin = desc.index("%BUILDDATE%") + len("%BUILDDATE%")
            end = desc.index("%", begin)
        except (AttributeError, IndexError):
            return "Not Found"

        builddate = desc[begin:end].strip()
        
        if builddate.isdigit():
            try:
                num = int(builddate)
                builddate = time.ctime(num)
            except ValueError:
                return builddate
        return builddate

    def _get_installdate(self, desc):
        try:
            begin = desc.index("%INSTALLDATE%") + len("%INSTALLDATE%")
            end = desc.index("%", begin)
        except (AttributeError, IndexError):
            return "Not Found"
        installdate = desc[begin:end].strip()
        
        if installdate.isdigit():
            num = int(installdate)
            installdate = time.ctime(num)
            return installdate
        return installdate

    def _get_reason(self, desc):            
        # There is no reason to extract anything from reason because if reason is in file
        # then this mean that package is installed by another package
        try:
            desc.index("%REASON%")
            pack_reason = ['Installed as a dependency for another package', False]
        except (AttributeError, IndexError, ValueError):
            pack_reason = ['Explicitly installed', True]
        
        return pack_reason
        
    def _get_description(self, desc):
        """Set description for the given pac"""
        try:
            begin = desc.index("%DESC%") + len("%DESC%")
            end = desc.index("%", begin)
            description = unicode(desc[begin:end].strip(), errors="ignore")
            return description
        except Exception:
            pass
        return ''

    def _get_dependencies(self, deps):
        """Set dependencies list for the given pac"""

        dependencies = []
        try:
            begin = deps.index("%DEPENDS%") + len("%DEPENDS%")
        except (AttributeError, IndexError, ValueError):
            return ""
        end = deps.find("%", begin) - len("%")
        dependencies = deps[begin:end].strip()
        depends = dependencies.split("\n")
        deps = ", ".join(depends)
        return deps
    
    def _get_req_by(self, depends):
        """Set list of packages that needs given pac"""
        
        try:
            begin = depends.index("%REQUIREDBY%") + len("%REQUIREDBY%")
        except Exception:
            return ''
        end = depends.find("%", begin) - len("%")
        reqs = depends[begin:end].strip().split("\n")
        req_by = ", ".join(reqs)
        return req_by

    def _get_provides(self, deps):
        
        try:
            begin = deps.index("%PROVIDES%") + len("%PROVIDES%")
        except ValueError:
            return
        end = deps.find("%", begin) - len("%")
        provides = deps[begin:end].strip().split("\n")
        provides = ", ".join(provides)
        
        return provides
        
    def _set_filelist(self, pac, files):
        """Set installed files list for the given pac"""
        if not pac.installed:
            return _("%s is not installed") %pac.name
        
        try:
            begin = files.index("%FILES%") + len("%FILES%")
            end = files.find("%", begin) - len("%")
            filelist = files[begin:end].strip()
            pac.filelist = filelist
        except (ValueError, AttributeError):
            return
        return
    
    def set_orphans(self):
        """Set orphans pacs"""

        for package in self["local"]:
            if package.prop_setted:
                continue
            else:
                raw_desc = self._get_raw_desc(package, "desc")
                package.explicitly = self._get_reason(raw_desc)[1]
            
            # Set orphans, if installed explicitly then continue
            if package.explicitly:
                continue
            else:
                package.req_by = self._search_dependencies(package)[1]
                if package.req_by:
                    package.isorphan = False
                else:
                    package.isorphan = True
                    #self.orphans.append(package)
            
        return
    
    def set_reason(self, repo):
        
        for pac in self["local"]:
            if pac.repo == repo:
                if pac.prop_setted:
                    continue
                else:
                    raw_desc = self._get_raw_desc(pac, "desc")
                    pac.explicitly = self._get_reason(raw_desc)[1]
                    if pac.explicitly:
                        for repo_pac in self[pac.repo]:
                            if repo_pac.name == pac.name:
                                repo_pac.explicitly[1] = True
        
    def get_by_name(self, name):
        """Return the pckage named 'name', or raise a NameError"""
        # First we search in 'local' repo
        for pac in self['local']:
            if name == pac.name:
                return pac
            
        for repo in sorted( self.repos.keys()):
            for pac in self[repo]:
                if name == pac.name:
                    return pac
        print "?? '%s' is not in the database..., trying advanced searching"  %name
        
        # If package is not found in first search because it name could be changed then
        # do more advanced search for package
        for repo in self.repos.keys():
            for pac in self[repo]:
                raw_depends = self._get_raw_desc(pac, "depends")
                provides = self._get_provides(raw_depends)
                
                if provides and name in provides:
                    print "... package found, '%s' name was changed to %s" %(name, pac.name)
                    return pac
            
        print "!! I really can't find package '%s'" %name
        return
    
    def set_olds(self):
        """Set old pacs"""
        for repo in self.repos.keys():
            if repo == "no_col":
                continue
            for pac in self[repo]:
                if pac.isold:
                    self.olds.append(pac)
                continue
            continue
        return
    
    def search_by_name_and_desc(self, key):
        """Return pacs which description match with desc"""
        pacs = []
        for repo in self.repos.keys():
            for pac in self[repo]:

                try:
                    pac.name.index(key)
                    pacs.append(pac)
                    continue
                except ValueError:
                    pass
                
                try:
                    try:
                        pac.description[0].lower().index(key)
                        pacs.append(pac)
                        continue
                    except ValueError:
                        continue
                except AttributeError:
                    d = self._get_raw_desc( pac, 'desc')
                    pac.description[0]= self._get_description( d)
                    try:
                        pac.description[0].lower().index(key)
                        pacs.append(pac)
                        continue
                    except ValueError:
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
        elif keywords.count("+"):
            keys = keywords.split("+")
        else:
            keys = keywords

        pacs = []
        #Then using get_by_desc and get_by_name get the packages
        if type(keys) == type(list()):
            for key in keys:
                pacs.extend(self.search_by_name_and_desc(key))
                continue
            for pac in pacs:
                if pacs.count(pac) == 1:
                    pacs.remove(pac)
                continue            
        else:
            pacs.extend(self.search_by_name_and_desc(keys))

        for pac in pacs:
            while pacs.count(pac) > 1:
                pacs.remove(pac)
                
        return pacs

    def get_local_file_deps(self, fname):
        from os import mkdir, system
        from os.path import exists
        from tarfile import TarFile
        from time import asctime, localtime

        if exists("/tmp/gtkpacman"):
           system("rm -rf /tmp/gtkpacman")

        mkdir("/tmp/gtkpacman", 0755)
        archive = TarFile.gzopen(fname)
        for member in archive.getmembers():
            archive.extract(member, "/tmp/gtkpacman")
            continue

        info_file = file("/tmp/gtkpacman/.PKGINFO")
        infos = info_file.read()
        info_file.close()

        infos_lines = infos.splitlines()
        deps = []
        conflicts = []
        
        for line in infos_lines:
            sides = line.split(" = ")
            if sides[0] == "depend":
                if sides[1]:
                    deps.append(sides[1])
            elif sides[0] == "conflict":
                if sides[1]:
                    conflicts.append(sides[1])
            continue

        system("rm -rf /tmp/gtkpacman")
        return deps, conflicts
    
    def refresh(self):
        """Refresh the database"""
        self.__init__()
