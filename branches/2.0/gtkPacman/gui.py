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

from thread import start_new_thread

import gettext

from gtk import main, main_quit
from gtk import TreeStore, TreeView, ListStore
from gtk import CellRendererText, CellRendererPixbuf
from gtk import ScrolledWindow
from gtk import STOCK_ADD, STOCK_GO_UP, STOCK_REMOVE
from gtk import RESPONSE_YES, RESPONSE_ACCEPT
from gtk.glade import XML

from dialogs import confirm_dialog, do_dialog, warning_dialog
from dialogs import about_dialog, non_root_dialog

class gui:
    def __init__(self, fname, database, uid):

        self.gld = XML(fname, "main_win", "gtkpacman")

        h_dict = {"quit":           self.quit,
                  "add_install":    self.add_to_install_queue,
                  "remove_install": self.remove_from_install_queue,
                  "add_remove":     self.add_to_remove_queue,
                  "remove_remove":  self.remove_from_remove_queue,
                  "execute":        self.execute,
                  #"up_sys":         self.upgrade_system,
                  #"refr_db":        self.refresh_databases,
                  #"add_local":      self.add_from_local_file,
                  #"clear_cache":    self.celar_cache,
                  #"empty_cache":    self.empty_cache,
                  #"search_pac":     self.search,
                  "show_popup":     self.show_popup,
                  "about":          self.about,
                  "pacs_changed":   self.pacs_changed,
                  "repo_changed":   self.repo_changed}
        self.gld.signal_autoconnect(h_dict)


        self.fname = fname
        self.database = database
        self.queues = {"add": [], "remove": []}

        self._setup_popup_menu(fname)
        self._setup_avaible_actions(uid)
        self._setup_repos_tree()
        self._setup_pacs_models()
        self._setup_pacs_tree()
        
        dlg = non_root_dialog()
        dlg.run()
        dlg.destroy()

    def _setup_avaible_actions(self, uid):
        if uid:
            self.gld.get_widget("queue").set_sensitive(False)
            self.gld.get_widget("immediate").set_sensitive(False)
            self.gld.get_widget("add_install").set_sensitive(False)
            self.gld.get_widget("remove_install").set_sensitive(False)
            self.gld.get_widget("add_remove").set_sensitive(False)
            self.gld.get_widget("remove_remove").set_sensitive(False)
            self.gld.get_widget("execute").set_sensitive(False)
            self.gld.get_widget("up_sys").set_sensitive(False)
            self.gld.get_widget("up_db").set_sensitive(False)
            self.popup_gld.get_widget("popup_add_install").set_sensitive(False)
            self.popup_gld.get_widget("popup_remove_install").set_sensitive(False)
            self.popup_gld.get_widget("popup_add_remove").set_sensitive(False)
            self.popup_gld.get_widget("popup_remove_remove").set_sensitive(False)

    def _adjust_queues (self):
        for name in self.queues["add"]:
            if name == "x-server":
                ind = self.queues["add"].index("x-server")
                self.queues["add"][ind] = "x-org"
            elif ">=" in name:
                ind = self.queues["add"].index(name)
                name = name.split(">=")[0]
                self.queues["add"][ind] = name
            continue

    def _adjust_names(self, names):
        for ind in range(len(names)):
            if names[ind] == "x-server":
                names[ind] = "xorg-server"
            elif ">=" in names[ind]:
                name = names[ind].split(">=")[0]
                names[ind] = name
            continue
        return names
        
    def _setup_pacs_tree(self):

        pacs_tree = self.gld.get_widget("pacs_tree")

        pacs_tree.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                                stock_id=0)
        pacs_tree.insert_column_with_attributes(-1, "", CellRendererPixbuf(),
                                                stock_id=1)
        pacs_tree.insert_column_with_attributes(-1, _("Package"),
                                                CellRendererText(), text=2)
        pacs_tree.insert_column_with_attributes(-1, _("Installed Version"),
                                                CellRendererText(), text=3)
        self.inst_ver_col = pacs_tree.insert_column_with_attributes(
            -1, _("Avaible Version"), CellRendererText(), text=4
            )
        self.repo_col = pacs_tree.insert_column_with_attributes(
            -1, _("Repo"),
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
            continue
        return

    def _setup_popup_menu(self, fname):
        self.popup_gld = XML(fname, "popup_menu", "gtkpacman")
        popup_h_dict = { "add_install": self.add_to_install_queue,
                         "remove_install": self.remove_from_install_queue,
                         "add_remove": self.add_to_remove_queue,
                         "remove_remove": self.remove_from_remove_queue }
        self.popup_gld.signal_autoconnect(popup_h_dict)
        self.popup = self.popup_gld.get_widget("popup_menu")

        
    def _setup_repos_tree(self):

        repos_tree = self.gld.get_widget("repos_tree")

        repos_model = TreeStore(str)
        all_it = repos_model.append(None, [_("All")])

        for repo in self.database.repos:
            if repo == "foreigners":
                continue
            repo_it = repos_model.append(all_it, [repo])
            repos_model.append(repo_it, [_("all")])
            repos_model.append(repo_it, [_("installed")])
            continue

        repos_model.append(all_it, [_("foreigners")])
        
        repos_tree.insert_column_with_attributes(-1, "", CellRendererText(),
                                                 text=0)
        repos_tree.set_model(repos_model)
        return

    def _setup_pacs_models(self):
        self.models = {}

        self.models["all"] = whole_list(self.database.values())
        try:
            self.models["foreigners"] = installed_list(self.database["foreigners"])
        except KeyError:
            self.database["foreigners"] = []
            self.models["foreigners"] = installed_list(self.database["foreigners"])
            
        for repo in self.database.repos:
            if repo == "foreigners":
                continue
            
            self.models[repo] = {}

            all_mod = all_list(self.database[repo])
            inst_mod = installed_list(self.database[repo])

            self.models[repo]["all"] = all_mod
            self.models[repo]["installed"] = inst_mod
            continue
        return

    def _refresh_trees(self):
        for model in self.models.keys():
            if model == "all" or model == "foreigners":
                self._refresh_model(model)
            else:
                for mod in self.models[model].keys():
                    self._refresh_model(model, mod)
                    continue
            continue
        return

    def _refresh_model(self, model, submodel=None):
        if submodel:
            liststore = self.models[model][submodel]
        else:
            liststore = self.models[model]

        for row in liststore:
            row[1] = None
            if row[2] in self.queues["add"]:
                row[0] = "green"
                row[3] = row[4]
            elif row[2] in self.queues["remove"]:
                row[0] = "red"
                row[3] = "-"
            continue
        return           

    def quit(self, widget, data=None):
        main_quit()
        return

    def repo_changed(self, widget, data=None):
        repos_tree = self.gld.get_widget("repos_tree")
        pacs_tree = self.gld.get_widget("pacs_tree")
        
        repos_model, tree_iter = repos_tree.get_selection().get_selected()
        selected = repos_model.get_value(tree_iter, 0)

        if not repos_model.iter_depth(tree_iter):
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
                    -1, _("Avaible Version"), CellRendererText(), text=4)
        pacs_tree.set_model(pacs_model)
        return

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
        return

    def add_to_install_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()

        name = model.get_value(l_iter, 2)
        if name in self.queues["add"]:
            return
        if name in self.queues["remove"]:
            self.queues["remove"].remove(name)

        self.queues["add"].append(name)

        image = model.get_value(l_iter, 0)
        if image == "red":
            model.set_value(l_iter, 1, STOCK_ADD)
        else:
            model.set_value(l_iter, 1, STOCK_GO_UP)
        return

    def remove_from_install_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()

        name = model.get_value(l_iter, 2)
        if not (name in self.queues["add"]):
            return

        self.queues["add"].remove(name)
        model.set_value(l_iter, 1, None)
        return

    def add_to_remove_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()

        name = model.get_value(l_iter, 2)
        if name in self.queues["remove"]:
            return
                
        image = model.get_value(l_iter, 0)

        if image == "red":
            return

        if name in self.queues["add"]:
            self.queues["add"].remove(name)

        self.queues["remove"].append(name)
        model.set_value(l_iter, 1, STOCK_REMOVE)
        return

    def remove_from_remove_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()

        name = model.get_value(l_iter, 2)
        if not (name in self.queues["remove"]):
            return

        self.queues["remove"].remove(name)
        model.set_value(l_iter, 1, None)
        return

    def execute(self, widget, data=None):
        pacs_queues = { "add": [], "remove": [] }
        
        for name in self.queues["add"]:
            pac = self.database.get_by_name(name)
            if not pac.prop_setted:
                self.database.set_pac_properties(pac)
                
            deps = pac.dependencies.split(", ")
            pacs_queues["add"].append(pac)
            pacs_queues["add"].extend(deps)
            continue

        for name in self.queues["remove"]:
            pac = self.database.get_by_name(name)
            if not pac.prop_setted:
                self.database.set_pac_properties(pac)
                
            if pac.req_by:
                req_pacs = []
                for req in pac.req_by.split(", "):
                    req_pac = self.database.get_by_name(req)
                    req_pacs.append(req_pac)
                    
                dlg = warning_dialog(self.gld.get_widget("main_win"),
                                     req_pacs)
                if dlg.run() == RESPONSE_YES:
                    pacs_queues["remove"].append(pac)
                    pacs_queues["remove"].extend(req_pacs)
                else:
                    self.queues["remove"].remove(name)
                dlg.destroy()
                continue
            pacs_queues["remove"].append(pac)
            continue

        if not (pacs_queues["add"] or pacs_queues["remove"]):
            self._refresh_trees_and_queues()
            return

        retcode = self._confirm(pacs_queues)
        if retcode:
            dlg = do_dialog(pacs_queues)
            dlg.connect("destroy", self._refresh_trees_and_queues)
            dlg.run()
        else:
            self.queues["add"] = []
            self.queues["remove"] = []
            self._refresh_trees_and_queues()
        return

    def _confirm(self, pacs_queues):
        dlg = confirm_dialog(self.gld.get_widget("main_win"), pacs_queues)
        retcode = dlg.run()
        dlg.destroy()
        return retcode

    def _refresh_trees_and_queues(self, widget=None):
        self._refresh_trees()
        self.queues["add"] = []
        self.queues["remove"] = []
        return
           
    def about(self, widget, data=None):
        dlg = about_dialog()
        dlg.run()
        dlg.destroy()
        return

    def show_popup(self, widget, event, data=None):
        if event.button == 3:
            self.popup.popup(None, None, None, event.button, event.time)
        else:
            self.popup.popdown()

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
