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

import os, string, re, time

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
        self.description = ""
        self.filelist = ""
        self.isorphan = True
        self.req_by = ""
        self.dependencies = ""
        self.prop_setted = False
	self.summary = ""
	# Flag is for marking package as " install as dependency ", ( flag = 11 )
	self.flag = None 
        
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
        self._get_pacman_version()
        self.repos = self._get_repos()

        self.set_pacs()
        self.repos.sort()
        self.repos.append("foreigners")

        #Init some variable which will be usefull
        self.olds = []
        self.orphans = []

    def _get_repos(self):
        conf_file = file("/etc/pacman.conf", "r").read()
        conf_file_lines = conf_file.splitlines()

        repos = [] 
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
                    repos.append(repo)
                continue
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
	self["local"] = []
        self.inst_pacs = self._get_installed()
        
        for repo in self.repos:
            self[repo] = []
            pacs = self._get_repo_pacs(repo)
            if not pacs:
                return
            
            for pac in pacs:
                pac_obj = self._make_pac(pac, repo)
		if pac_obj.installed:
		    self[repo].append(pac_obj)
		    ver = pac_obj.inst_ver
		    pac_local = package(pac_obj.name, ver, inst_ver=ver, repo='local', inst=True, isold=False)
		    self["local"].append(pac_local)
		else:
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
	    raw_desc = self._get_raw_desc(pac, "desc")
	    raw_depends = self._get_raw_desc(pac, "depends")
	    raw_files = self._get_raw_desc(pac, "files")
	    
	    pac.req_by = self._search_reqby(pac.name)
	    self._set_filelist(pac, raw_files)
	else:
	    raw_desc = self._get_raw_desc(pac, "desc")
	    raw_depends = self._get_raw_desc(pac, "depends")
	
	if raw_desc:
	    self._set_summary(pac, raw_desc, raw_depends)
	else:
	    return
        
        pac.prop_setted = True
    
    def _set_summary(self, pac, raw_desc, raw_depends=None):
        
        desc = self._get_description(raw_desc)
        deps = self._get_dependencies(raw_depends)
        size = self._get_size(raw_desc)

        if pac.installed:
	    if not pac.req_by:
		pac.req_by = self._get_req_by(raw_depends)
            packager = self._get_packager(raw_desc)
            builddate = self._get_builddate(raw_desc)
            installdate = self._get_installdate(raw_desc)
            reason = self._get_reason(raw_desc)
            #summary = _("Description: %s\nDepends on: %s\nRequired by: %s\nSize: %s\nPackager: %s\nBuilt: %s\nInstalled: %s\nReason: %s") %(desc, deps, pac.req_by, size, packager, builddate, installdate, reason)
	    summary = ":: %s" %( desc ),\
		    ":: %s"%( deps ),\
		    ":: %s" %( pac.req_by ),\
		    ":: %s" %( packager ),\
		    ":: %s" %( builddate ),\
		    ":: %s" %( installdate ),\
		    ":: %s" %( size),\
		    ":: %s" %( reason )

        else:
            #summary = _("Description: %s\nDepends on: %s\nSize (compressed): %s") %(desc, deps, size)
	    summary = ":: %s" %( desc ),\
		    ":: %s" %( deps ),\
		    ":: %s" %( size )

        pac.summary = summary
        pac.dependencies = deps
        #pac.description = desc
	
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
        except ValueError:
            begin = desc.index("%SIZE%") + len("%SIZE%")

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
        begin = desc.index("%PACKAGER%") + len("%PACKAGER%")
        end = desc.index("%", begin)

        packager = desc[begin:end].strip()
        return packager

    def _get_builddate(self, desc):
        begin = desc.index("%BUILDDATE%") + len("%BUILDDATE%")
        end = desc.index("%", begin)

        builddate = desc[begin:end].strip()
	
	if builddate.isdigit():
	    try:
		num = int(builddate)
		builddate = time.ctime(num)
	    except ValueError:
		return builddate
        return builddate

    def _get_installdate(self, desc):
        begin = desc.index("%INSTALLDATE%") + len("%INSTALLDATE%")
        end = desc.index("%", begin)

        installdate = desc[begin:end].strip()
	
	if installdate.isdigit():
	    num = int(installdate)
	    installdate = time.ctime(num)
	    return installdate
        return installdate

    def _get_reason(self, desc):
        try:
            begin = desc.index("%REASON%") + len("%REASON%")
            reason_int = int(desc[begin:].strip())

            if reason_int:
                reason = _("Installed as a dependency for another package")
            else:
                reason = _("Explicitly installed")

            return reason
        except Exception:
            return ("Explicitly installed")
        
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
        except ValueError:
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
            end = depends.find("%", begin) - len("%")
        except Exception:
            return ''
        
        reqs = depends[begin:end].strip().split("\n")
        req_by = ", ".join(reqs)
        return req_by

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
	print "Info: %s is not in the database..."  %name
	return

    def search_by_name(self, name):
        """Return a list of packages wich contains 'name' in the name"""
        pacs = []
        for repo in self.repos:
            for pac in self[repo]:
                if pac.name.count(name):
                    pacs.append(pac)
                continue
            continue
        return pacs
    
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
    
    def _search_reqby(self, pac_name):
	# Search in local repo for pac_name in descriptions files. 
	# If found than pack.name is requied by pack_name
	stack = []
	req_by = ''
	req = ""
	for package in self["local"]:
	    if not package.req_by:
		raw_desc = self._get_raw_desc(package, "depends")
		req_by = self._get_dependencies(raw_desc)
	    for p in req_by.split(','):
		p = p.strip()
		if '=<' in p:
		    p = p.split('=<')[0]
		if '>=' in p:
		    p = p.split('>=')[0]
		if p == pac_name and package.name not in stack and package.name != pac_name:
		    stack.append(package.name)
	if stack:
	    for name in stack:
		req = req + ", " + name
	    req = req[2:]
	return req
    
    def get_by_desc(self, desc):
        """Return pacs which description match with desc"""
        pacs = []
        for repo in self.repos:
            for pac in self[repo]:
		if not pac.description:
		    d = self._get_raw_desc( pac, 'desc')
		    pac.description = self._get_description( d)
		if pac.description.count(desc):
		    pacs.append(pac)
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
                pacs.extend(self.search_by_name(key))
                pacs.extend(self.get_by_desc(key))
                continue
            for pac in pacs:
                if pacs.count(pac) == 1:
                    pacs.remove(pac)
                continue
            
        else:
            pacs.extend(self.search_by_name(keys))
            pacs.extend(self.get_by_desc(keys))

        for pac in pacs:
            while pacs.count(pac) > 1:
                pacs.remove(pac)
                continue
            continue
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
