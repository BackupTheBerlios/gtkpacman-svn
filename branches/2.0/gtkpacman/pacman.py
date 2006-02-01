from os import listdir

from libpypac import libpypac_0, libpypac_1, libpypac_2, libpypac_3
from libpypac import libpypac_misc

#constants
global NAME, VERSION, REPO, LOCAL, REMOTE, reasons
NAME = "name"
VERSION = "version"
REPO = "repo"
LOCAL = "local"
REMOTE = "remote"
reasons = {"Explicitly installed": 0, "Installed as dependency": 1}

#Basic pacman variables
global servers, repos, noup, ignore, hold
servers, repos, noup, ignore, hold = libpypac_0.read_conf()

#Definition of the packaes dictionary
global packages
packages = {"remote": {}, "local": {"none": {}}}
for repo in repos:
    packages["remote"][repo] = {}
    packages["local"][repo] = {}
    continue

#Indicator, if true packages are already all done.
global written
written = False

#Utilities
global inst_names, inst_packs
inst_names = []
inst_packs = {}

def _get_local():
    global inst_names, inst_packs
    for pac in listdir("/var/lib/pacman/local"):
        ([name, version, desc, url, packager, blt, instd, size, reason],
         depends, dependants, files) = libpypac_1.loc_pack_info(pac)
        package = {"version": version, "desc": desc,
                   "url": url, "packager": packager, "built": blt,
                   "install_date": instd, "size": int(size),
                   "reason": reasons[reason], "dependencies": depends,
                   "dependants": dependants, "file_list": files}
        inst_packs[name] = package
        inst_names.append(name)
        continue
    return

def _parse_repo(repo):
    global packages, LOCAL, VERSION, REMOTE, inst_names
    
    for pac in listdir("/var/lib/pacman/%s" %repo):
        ([name, version, desc, size],
         dependencies) = libpypac_1.pack_info(pac, repo)
        if name in inst_names:
            #If the packages is already installed insert its
            #description in the LOCAL area of the dictionary, under
            #the repo to which it belongs. Then compare version,
            #and set the old attribute. In the end, copy the
            #package description also in the REMOTE...
            packages[LOCAL][repo][name] = inst_packs[name]
            if version > packages[LOCAL][repo][name][VERSION]:
                old = True
            else:
                old = False

            packages[LOCAL][repo][name]["old"] = old
            packages[REMOTE][repo][name] = packages[LOCAL][repo][name]
            inst_names.remove(name)
                
        else:
            #...else write a new description and insert it into
            #REMOTE
            package = {"version": version, "desc": desc,
                       "size": int(size), "dependencies": dependencies,
                       "old": False}
            packages[REMOTE][repo][name] = package
        continue
            
def get_all():
    global written, repo, inst_names, LOCAL, VERSION, packages, REMOTE
    """Explore the repos tree and build the packages tree"""
    # Find already installed packages
    _get_local()
        

    #Parse the local database
    for repo in repos:
        if not packages[REMOTE][repo]:
            _parse_repo(repo)
        continue
                          
    for pac in inst_names:
        #Now insert in the LOCAL the installed packages which don't belong
        #to any repo
        packages[LOCAL]["none"][pac] = inst_packs[pac]
        continue

    #Finally return the packages dict.
    return packages

