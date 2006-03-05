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

from gtk import main, main_quit
from gtk import TreeStore, TreeView, ListStore
from gtk import CellRendererText, CellRendererPixbuf
from gtk import ScrolledWindow
from gtk.glade import XML

class gui:
    def __init__(self, fname, database):

        self.gld = XML(fname, "main_win")

        h_dict = {"quit":           self.quit,
                  #"add_install":    self.add_to_install_queue,
                  #"remove_install": self.remove_from_install_queue,
                  #"add_remove":     self.add_to_remove_queue,
                  #"remove_remove":  self.remove_from_remove_queue,
                  #"execute":        self.execute,
                  #"up_sys":         self.upgrade_system,
                  #"refr_db":        self.refresh_databases,
                  #"add_local":      self.add_from_local_file,
                  #"clear_cache":    self.celar_cache,
                  #"empty_cache":    self.empty_cache,
                  #"about":          self.about,
                  "pacs_changed": self.pacs_changed,
                  "repo_changed":   self.repo_changed}
        self.gld.signal_autoconnect(h_dict)


        self.fname = fname
        self.database = database

        self._setup_repos_tree()
        self._setup_pacs_models()
        self._setup_pacs_tree()


    def _setup_pacs_tree(self):

        pacs_tree = self.gld.get_widget("pacs_tree")

        pacs_tree.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                                stock_id=0)
        pacs_tree.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                                stock_id=1)
        pacs_tree.insert_column_with_attributes(-1, "Package",
                                                CellRendererText(), text=2)
        pacs_tree.insert_column_with_attributes(-1, "Installed Version",
                                                CellRendererText(), text=3)
        self.inst_ver_col = pacs_tree.insert_column_with_attributes(
            -1, "Avaible Version", CellRendererText(), text=4
            )
        self.repo_col = pacs_tree.insert_column_with_attributes(
            -1, "Repo",
            CellRendererText(), text=5
            )

        pacs_tree.set_model(self.models["all"])

        sort_id = 0
        for col in pacs_tree.get_columns():
            col.set_reorderable(True)
            col.set_sort_column_id(sort_id)
            col.set_clickable(True)
            col.set_resizable(True)
            sort_id += 1
        
    def _setup_repos_tree(self):

        repos_tree = self.gld.get_widget("repos_tree")

        repos_model = TreeStore(str)
        all_it = repos_model.append(None, ["All"])

        for repo in self.database.repos:
            repo_it = repos_model.append(all_it, [repo])
            if repo != "foreigners":
                repos_model.append(repo_it, ["all"])
                repos_model.append(repo_it, ["installed"])
            continue
        
        repos_tree.insert_column_with_attributes(-1, "", CellRendererText(),
                                                 text=0)
        repos_tree.set_model(repos_model)
        return

    def _setup_pacs_models(self):
        self.models = {}

        self.models["all"] = whole_list(self.database.values())
        self.models["foreigners"] = installed_list(self.database["foreigners"])
        
        for repo in self.database.repos:
            if repo == "foreigners":
                continue
            
            self.models[repo] = {}

            all_mod = all_list(self.database[repo])
            inst_mod = installed_list(self.database[repo])

            self.models[repo]["all"] = all_mod
            self.models[repo]["installed"] = inst_mod

    def quit(self, widget, data=None):
        main_quit()

    def repo_changed(self, widget, data=None):
        repos_tree = self.gld.get_widget("repos_tree")
        pacs_tree = self.gld.get_widget("pacs_tree")
        
        repos_model, tree_iter = repos_tree.get_selection().get_selected()
        selected = repos_model.get_value(tree_iter, 0)

        if selected == "All":
            pacs_model = self.models["all"]
            if not self.repo_col:
                self.repo_col = pacs_tree.insert_column_with_attributes(
                    -1, "", CellRendererText(), text=5
                    )
            if not self.inst_ver_col:
                self.inst_ver_col = pacs_tree.insert_column_with_atrributes(
                    -1, "", CellRendererText(), text=4
                    )
                
        elif selected == "foreigners":
            if self.repo_col:
                pacs_tree.remove_column(self.repo_col)
                self.repo_col = None
                
            if self.inst_ver_col:
                pacs_tree.remove_column(self.inst_ver_col)
                self.inst_ver_col = None
            
            pacs_model = self.models[selected]
            
        else:
            if selected == "all" or selected == "installed":
                parent_iter = repos_model.iter_parent(tree_iter)
                parent = repos_model.get_value(parent_iter, 0)
                pacs_model = self.models[parent][selected]
            else:
                pacs_model = self.models[selected]["all"]

            if self.repo_col:
                pacs_tree.remove_column(self.repo_col)
                self.repo_col = None
            if not self.inst_ver_col:
                self.inst_ver_col = pacs_tree.insert_column_with_attributes(
                    -1, "Avaible Version", CellRendererText(), text=4)
        pacs_tree.set_model(pacs_model)

    def pacs_changed(self, widget, data=None):
        sum_txt = self.gld.get_widget("summary")
        sum_buf = sum_txt.get_buffer()

        file_txt = self.gld.get_widget("files")
        file_buf = file_txt.get_buffer()
        
        model, t_iter = widget.get_selection().get_selected()
        name = model.get_value(t_iter, 2)

        pac = self.database.get_by_name(name)
        if not pac.prop_setted:
            self.database.set_pac_properties(pac)

        sum_buf.set_text(pac.summary)
        file_buf.set_text(pac.filelist)

class installed_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str)

        for pac in pacs:
            if not pac.installed:
                continue

            if pac.isold:
                image = "yellow"
            else:
                image = "green"
                
            self.append([image, None, pac.name, pac.inst_ver, pac.version])
            continue

class all_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str)

        for pac in pacs:
            if not (pac.isold or pac.installed):
                image = "red"
                inst_ver = "-"
            elif pac.isold:
                image = "yellow"
                inst_ver = pac.inst_ver
            else:
                image = "green"
                inst_ver = pac.inst_ver

            self.append([image, None, pac.name, inst_ver, pac.version])
            continue

class whole_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str, str)
        
        for r_list in pacs:
            for pac in r_list:
                if not (pac.isold or pac.installed):
                    image = "red"
                    inst_ver = "-"
                elif pac.isold:
                    image = "yellow"
                    inst_ver = pac.inst_ver
                else:
                    image = "green"
                    inst_ver = pac.inst_ver

                self.append([image, None, pac.name, inst_ver, pac.version, pac.repo])
