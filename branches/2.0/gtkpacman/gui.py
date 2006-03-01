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
                  #"repo_changed":   self.repo_changed
                  }
        self.gld.signal_autoconnect(h_dict)


        self.fname = fname
        self.database = database

        self._setup_repos_tree()
        self._setup_repos_notebook()

    def _setup_repos_tree(self):

        repos_tree = self.gld.get_widget("treeview")

        repos_model = TreeStore(str)
        all_it = repos_model.append(None, ["All"])

        for repo in self.database.repos:
            repo_it = repos_model.append(all_it, [repo])
            repos_model.append(repo_it, ["all"])
            repos_model.append(repo_it, ["installed"])
            continue
        
        repos_tree.insert_column_with_attributes(-1, "", CellRendererText(),
                                                 text=0)
        repos_tree.set_model(repos_model)
        return

    def _setup_repos_notebook(self):
        notebook = self.gld.get_widget("notebook")
        self.pages = {}

        for repo in self.database.repos:
            
            page = notebook_page(repo)
            page.tree.set_model(self.database[repo])
            notebook.append_page(page)

            inst_page = notebook_page(repo)
            inst_page.tree.set_model(self.database[repo], True)
            notebook.append_page(inst_page)

            self.pages[repo] = {}
            self.pages[repo]["all"] = page
            self.pages[repo]["installed"] = inst_page
            continue
        return

    def quit(self, widget, event=None):
        main_quit()

class notebook_page(ScrolledWindow):

    def __init__(self, repo):
        ScrolledWindow.__init__(self)
        self.set_policy("automatic", "automatic")
        
        self.tree = tree()
        self.add(self.tree)

        self.show_all()


class tree(TreeView):

    def __init__(self):

        TreeView.__init__(self)

        self.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                           stock_id=0)
        self.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                           stock_id=1)
        self.insert_column_with_attributes(-1, "Package", CellRendererText(),
                                           text=2)
        self.insert_column_with_attributes(-1, "Installed Version",
                                           CellRendererText(), text=3)
        self.insert_column_with_attributes(-1, "Version Avaible",
                                           CellRendererText(), text=4)

        col_id = 0
        for col in self.get_columns():
            col.set_reorderable(True)
            col.set_clickable(True)
            col.set_sort_column_id(col_id)
            col.set_resizable(True)
            col_id += 1
            continue
        self.set_enable_search(True)
        self.set_reorderable(True)
            

    def set_model(self, pacs, installed=False):
        if installed:
            self.model = installed_list(pacs)
        else:
            self.model = all_list(pacs)

        TreeView.set_model(self, self.model)

class installed_list(ListStore):

    def __init__(self, pacs):

        ListStore.__init__(self, str, str, str, str, str)

        for pac in pacs:
            if not pac.installed:
                continue

            if pac.isold:
                image = "yellow"
                ver = pac.version
            else:
                image = "green"
                ver = None

            self.append([image, None, pac.name, pac.inst_ver, ver])
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
