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
                    db_ver = libpypac_1.pack_info(pack, repo)[0][1]
                    self[repo][infos[0]] = [infos, deps, req_by, files, db_ver]
                else:
                    try:
                        (infos, deps) = libpypac_1.pack_info(pack, repo)
                    except:
                        continue
                    self[repo][infos[0]] = [infos, deps]
                continue
            continue
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
                return None
