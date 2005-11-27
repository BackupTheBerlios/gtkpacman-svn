import os, thread

from libpypac import libpypac_0, libpypac_1, libpypac_2, libpypac_3
from libpypac import libpypac_misc

class database(dict):

    def __init__(self):
        dict.__init__(self)

        (self.servers,
         self.repos,
         self.noup,
         self.ignore,
         self.hold) = libpypac_0.read_conf()

        self.repos.sort()

    def setup_pacs(self, pack_cbk=None, repo_cbk=None):
        
        for repo in self.repos:

            self[repo] = {}
            
            repo_pacs = os.listdir("%s%s" %(libpypac_0.root_dir, repo))
            repo_pacs.sort()
            fraction = 1.0/len(repo_pacs)
            
            try:
                repo_pacs.remove(".lastupdate")
            except ValueError:
                pass

            for pack in repo_pacs:

                try:
                    (infos, deps) = libpypac_1.pack_info(pack, repo)
                except:
                    continue

                (inst_infos,
                 inst_deps,
                 req_by,
                 files) = libpypac_1.loc_pack_info_name(infos[0])
                if type(inst_infos) is type(None):
                    installed = False
                else:
                    installed = True

                if installed:
                    db_ver = infos[1]
                    if infos[1] > inst_infos[1]:
                        old = True
                    else:
                        old = False
                                       
                    self[repo][infos[0]] = [inst_infos, inst_deps, req_by,
                                            files, db_ver, repo, old]
                else:
                    self[repo][infos[0]] = [infos, deps, repo]

                if type(pack_cbk) is not type(None):
                    pack_cbk(fraction, repo, infos[0])
                continue
            if type(repo_cbk) is not type(None):
                repo_cbk(repo)
            continue
        self._set_third_pacs(pack_cbk, repo_cbk)
        return
    
    def get_by_name(self, name, repo=None):
        
        if not repo:
            for repo in self.keys():
                try:
                    return self[repo][name]
                except KeyError:
                    continue

        else:
            try:
                return self[repo][name]
            except KeyError:
                return False
        return False

    def _set_third_pacs(self, pack_cbk=None, repo_cbk=None):

        self["third"] = {}
        local_list = os.listdir("%s/local" %libpypac_0.root_dir)

        fraction = 1.0/len(local_list)

        for pac in local_list:
            (infos, deps, req_by, files) =  libpypac_1.loc_pack_info(pac)
            if not self.get_by_name(infos[0]):
                self["third"][infos[0]] = [
                    infos, deps, req_by, files, "-", "-", False
                    ]
            if type(pack_cbk) is not type(None):
                pack_cbk(fraction, "Thirds' packages", infos[0])
            continue
        if type(repo_cbk) is not type(None):
            repo_cbk("third")
        return

class pacman:

    def __init__(self, gui):

        self.db = database()
        self.servers = self.db.servers
        self.repos = self.db.repos
        self.noup = self.db.noup
        self.ignore = self.db.ignore
        self.hold = self.db.hold
        self.gui = gui

    def sync_pack(self, pack):

        name = pack[0][0]
        retcode, repo, pack, cache, size = libpypac_2.exist_check(name,
                                                                  self.repos)
        if not retcode:
            self.gui.err_cbk("%s cannot be found in the database" %pack)
            return

        pacs, deps, err, conflict, tot_size = libpypac_2.dep_install(
            [name],
            self.repos
            )

        to_install = self.check_installed(pacs)
        retcode = self.gui.question(to_install)
        if not retcode:
            return
        
        retcode, package, error = self.download(to_install)
        if not retcode:
            self.gui.err_cbk("%s cannot be downloaded%s" %(package, error))
            return

        self.install(to_install, deps)

    def check_installed(self, pacs):

        to_install = []

        for pac in pacs:
            name, version, rel = libpypac_misc.get_name(pac)
            retcode, dep_list, old_reason, old_ver = libpypac_3.old_check(name)
            if not retcode:
                to_install.append(pac)
            elif version > old_ver:
                to_install.append(pac)
            else:
                pass
            continue

        return to_install

    def download(self, to_install):

        for pac in to_install:
            name = libpypac_misc.get_name(pac)[0]
            retcode, repo, pack, cache, size = libpypac_2.exist_check(
                name,
                self.repos
                )

            if not cache:
                thread.start_new_thread(libpypac_0.download,
                                        (self.servers,
                                         repo, pac,
                                         size,
                                         self.gui.down_cbk))
                retcode = libpypac_2.exist_check(name, self.repos)[3]
                if not retcode:
                    return (False, pac, "")

                self.gui.md5sum_start(pac)
                retcode = libpypac_0.md5sum_check(repo, pac)
                self.gui.md5sum_stop()
                if not retcode:
                    return (False, pac, "md5sum check failed")

            else:
                self.gui.already(pac)

            return(True, None, None)

        def install(self, to_install, deps):
            for pac in to_install:
                name = libpypac_misc.get_name(pac)[0]

                pack, old_dep, old_reason, old_ver = libpypac_3.old_check(name)

                if pack:
                   reason = old_reason
                else:
                    if libpypac_misc.get_name(pac)[0] in deps:
                        reason = 0

                conflicts = libpypac_2.file_conflict_check([pac], None)[0]
                if conflicts:
                    files = ""
                    for file in conflicts:
                        files += file+" "
                    self.gui.err_cbk("File conflicts found: %s" %files)

                
                libpypac_2.install(pac, name, old_dep, self.noup, reason,
                                   old_ver, None)
                continue
            return
