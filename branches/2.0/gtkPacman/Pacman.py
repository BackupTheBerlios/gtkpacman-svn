import os

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

    def setup_pacs(self): #, pac_cbk, repo_cbk):
        
        for repo in self.repos:

            self[repo] = {}
            #self.installed = []

            repo_pacs = os.listdir("%s%s" %(libpypac_0.root_dir, repo))
            repo_pacs.sort()
            fraction = 1.0/len(repo_pacs)
            
            try:
                repo_pacs.remove(".lastupdate")
            except ValueError:
                pass

            for pack in repo_pacs:
                
                installed = True
                try:
                    (infos,
                     deps,
                     req_by,
                     files) = libpypac_1.loc_pack_info(pack)
                except:
                    installed = False

                if installed:
                    try:
                        db_ver = libpypac_1.pack_info(pack, repo)[0][1]
                    except:
                        db_ver = "-"
                        
                    self[repo][infos[0]] = [infos, deps, req_by, files, db_ver]
                    #self.installed.append(pack)
                else:
                    try:
                        (infos, deps) = libpypac_1.pack_info(pack, repo)
                    except:
                        continue
                    self[repo][infos[0]] = [infos, deps]
                continue
            continue
        self._set_third_pacs()
        self._set_olds()
        return
    
    def get_by_name(self, name, repo=None):
        
        if not repo:
            for repo in self.repos:
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

    def _set_third_pacs(self):

        self["third"] = {}
        local_list = os.listdir("%s/local" %libpypac_0.root_dir)

        for pac in local_list:
            (infos, deps, req_by, files) =  libpypac_1.loc_pack_info(pac)
            if not self.get_by_name(infos[0]):
                self["third"][infos[0]] = [infos, deps, req_by, files, "-"]
            continue
        return

    def _set_olds(self):

        for repo in self.repos:
            for pac in self[repo].values():
                if len(pac) < 2:
                    continue

                pack_name = "-".join((pac[0][0], pac[0][1]))
                loc_ver = pac[0][1]
                rem_ver = libpypac_1.pack_info(pack_name, repo)[0][1]

                if loc_ver < rem_ver:
                    pac.append(True)
                else:
                    pac.append(False)
