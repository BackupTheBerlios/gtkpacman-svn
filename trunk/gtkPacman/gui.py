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

import gettext, gobject, pango

from gtk import main, main_quit, TreeStore, TreeView, ListStore, Button
from gtk import CellRendererText, CellRendererPixbuf, ScrolledWindow
from gtk import STOCK_ADD, STOCK_GO_UP, STOCK_REMOVE, STOCK_CLOSE
from gtk import RESPONSE_YES, RESPONSE_ACCEPT, RESPONSE_OK, RESPONSE_NO
from gtk import TextBuffer, TextTag
from gtk.gdk import pixbuf_new_from_file, Cursor, WATCH
from gtk.glade import XML

from dialogs import non_root_dialog, about_dialog, warning_dialog, do_dialog 
from dialogs import confirm_dialog, search_dialog, upgrade_dialog
from dialogs import upgrade_confirm_dialog, local_install_dialog, info_dialog
from dialogs import local_install_fchooser_dialog, local_confirm_dialog
from dialogs import command_dialog, error_dialog, ignorepkg_dialog
from dialogs import holdpkg_dialog, choose_pkgbuild_dialog, change_user_dialog

from models import installed_list, all_list, whole_list, search_list, file_list

#from threading import Thread

class gui:
    def __init__(self, fname, database, uid, icon):

        # Setup the main gui: read glade file, connect signals
        self.gld = XML(fname, "main_win", "gtkpacman")
        self.gld.get_widget("main_win").set_icon(pixbuf_new_from_file(icon))

        h_dict = {"quit":           self.quit,
                  "add_install":    self.add_to_install_queue,
                  "remove_install": self.remove_from_install_queue,
                  "add_remove":     self.add_to_remove_queue,
                  "remove_remove":  self.remove_from_remove_queue,
                  "execute":        self.execute,
                  "up_sys":         self.upgrade_system,
                  "refr_db":        self.refresh_database,
                  "add_local":      self.add_from_local_file,
                  "clear_cache":    self.clear_cache,
                  "empty_cache":    self.empty_cache,
                  "search_pac":     self.search,
                  "show_popup":     self.show_popup,
                  "about":          self.about,
                  "pacs_changed":   self.pacs_changed,
                  "repo_changed":   self.repo_changed,
                  "make_pkg":       self.make_package}
        self.gld.signal_autoconnect(h_dict)


        self.fname = fname
        self.icon = icon
        self.database = database
        self.queues = {"add": [], "remove": []}
        self.search_iter = None

        #Setup secondary gui elements
        self._setup_popup_menu(fname)
        self._setup_repos_tree()
        self._setup_pacs_models()
        self._setup_pacs_tree()
        self._setup_files_tree()

        #Setup statusbar
	self._statusbar()
	
	#gobject.timeout_add( 3000, self._on_idle, gobject.PRIORITY_LOW)
	#gobject.idle_add(self._on_idle)

        #Check if root, else notufy it and deactivate some widgets
        if uid:
            self._setup_avaible_actions()
            dlg = non_root_dialog(icon)
            dlg.run()
            dlg.destroy()

    def _setup_avaible_actions(self):
        #Deactivate some widgets. Called if not root
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
	pacs_tree.set_reorderable(False)

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

        pacs_tree.set_model(self.models[_("All")])

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
                         "remove_remove": self.remove_from_remove_queue,
                         "search": self.search }
        self.popup_gld.signal_autoconnect(popup_h_dict)
        self.popup = self.popup_gld.get_widget("popup_menu")

        
    def _setup_repos_tree(self):

        repos_tree = self.gld.get_widget("repos_tree")
                
        repos_tree.insert_column_with_attributes(-1, "", CellRendererText(),
                                                 text=0)
        repos_tree.set_model(self._make_repos_model())
        return
    
    def _setup_files_tree(self):

        file_tree = self.gld.get_widget("files")
        file_tree.insert_column_with_attributes(-1, "", CellRendererText(),
                                                text=0)
        return
    
    def _setup_pacs_models(self):
        self.models = {}

        self.models[_("All")] = whole_list(self.database.values())
        try:
            self.models[_("foreigners")] = installed_list(self.database["foreigners"])
        except KeyError:
            self.database["foreigners"] = []
            self.models[_("foreigners")] = installed_list(self.database["foreigners"])
            
        for repo in self.database.keys():
            if repo == _("foreigners"):
                continue
            
            self.models[repo] = {}

            all_mod = all_list(self.database[repo])
            inst_mod = installed_list(self.database[repo])

            self.models[repo][_("all")] = all_mod
	    if repo != _('local'):
		self.models[repo][_("installed")] = inst_mod
            continue
        return

    def _make_repos_model (self):
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
        return repos_model
 
    def _pacs_tree_exp_check(self):
        expanded= []
        def expander_check(model, path, iter):
            is_expanded = repos_tree.row_expanded(path)
            if is_expanded:
                expanded.append(path)

        repos_tree = self.gld.get_widget("repos_tree")
        model = repos_tree.get_model()
        iter = model.get_iter_root()
        path = model.get_path(iter)
        model.foreach(expander_check)
        return expanded

    def _refresh_repos_tree (self):            
        expanded = self._pacs_tree_exp_check()
        
        repos_tree = self.gld.get_widget("repos_tree")
        repos_tree.set_model(self._make_repos_model())
        
        for row in expanded:
            repos_tree.expand_row(row, False)
        return

    def _refresh_trees(self):
        for model in self.models.keys():
	    if model == _("All") or model == _("foreigners") or model == _("search"):
                self._refresh_model(model)
            else:
                try:
                    for mod in self.models[model].keys():
                        self._refresh_model(model, mod)
                        continue
                except AttributeError:
                    pass
            continue
        return

    def _refresh_model(self, model, submodel=None):
        if submodel:
            liststore = self.models[model][submodel]
        else:
            liststore = self.models[model]

        for row in liststore:
            row[1] = None
            check = row[2][:]
            if check in self.queues["remove"] and model ==  _("foreigners"):
                nr = 0
                for rm in liststore:
                    nr += 1
                    if check == rm[2]:
                        del liststore[nr -1]
            elif check in self.queues["remove"] and submodel ==  _("installed"):
		itr = liststore.get_iter_first()
		while itr:
		    rm = liststore.get_value(itr, 2)
		    # We delete row if match
		    if check == rm:
			liststore.remove(itr)
		    itr = liststore.iter_next(itr)
            elif row[2] in self.queues["add"] and row[0] == 'red' and submodel =="all":
                row[0] = "green"
                row[3] = row[4]
                self.models[model]["installed"].append(row)
            elif row[2] in self.queues["add"]:
                row[0] = "green"
                row[3] = row[4]
            elif row[2] in self.queues["remove"]:
                row[0] = "red"
                row[3] = "-"
            continue
        return
    
    def _refresh_trees_and_queues(self, widget=None, pacs_queues=None):
        self.database.refresh()
        self._refresh_repos_tree()
        
        if pacs_queues:
            for pac in pacs_queues["add"]:
                if not pac.name in self.queues["add"]:
                    self.queues["add"].append(pac.name)
	    for pac in pacs_queues["remove"]:
                if not pac.name in self.queues["remove"]:
                    self.queues["remove"].append(pac.name)

        self._refresh_trees()
        self.queues["add"] = []
        self.queues["remove"] = []
        if pacs_queues:
            for pac in pacs_queues["add"]:
                pac.installed = True
                pac.inst_ver = pac.version
                self.database.set_pac_properties(pac)
                continue
            for pac in pacs_queues["remove"]:
                pac.installed = False
                if pac.repo == 'foreigners':
                    del pac
                    continue
                self.database.set_pac_properties(pac)
                continue
            sum_txt = self.gld.get_widget("summary")
            file_tree = self.gld.get_widget("files")
            sum_buf = sum_txt.get_buffer()
            tree = file_tree.get_model()
            
            try:
                #sum_buf.set_text(pac.summary)
		self._set_pac_summary(pac)
                file_model = file_list(pac.filelist)
                file_tree.set_model(file_model)
            except:
                col = file_tree.get_columns()
                tree.clear()
                sum_buf.set_text('')
            
        del(pacs_queues)
	self._statusbar()
	self.gld.get_widget("main_win").set_sensitive(True)
	
    
    #----------------------------- Callbacks ------------------------------#
    def show_popup(self, widget, event, data=None):
        if event.button == 3:
            self.popup.popup(None, None, None, event.button, event.time)
        else:
            self.popup.popdown()
	    
    def repo_changed(self, widget, data=None):
        repos_tree = self.gld.get_widget("repos_tree")
        pacs_tree = self.gld.get_widget("pacs_tree")
        
        repos_model, tree_iter = repos_tree.get_selection().get_selected()
        selected = repos_model.get_value(tree_iter, 0)

        if not repos_model.iter_depth(tree_iter):
            if selected.count(_("Search")):
                pacs_model = self.models["search"]
            else:
                pacs_model = self.models[_("All")]
            if not self.repo_col:
                self.repo_col = pacs_tree.insert_column_with_attributes(
                    -1, _("Repo"), CellRendererText(), text=5
                    )
            if not self.inst_ver_col:
                self.inst_ver_col = pacs_tree.insert_column_with_attributes(
                    -1, _("Available Version"), CellRendererText(), text=4
                    )
                
        elif selected == _("foreigners"):
            if self.repo_col:
                pacs_tree.remove_column(self.repo_col)
                self.repo_col = None
                
            if self.inst_ver_col:
                pacs_tree.remove_column(self.inst_ver_col)
                self.inst_ver_col = None
            
            pacs_model = self.models[selected]
            
        else:
            if selected == _("all") or selected == _("installed"):
                parent_iter = repos_model.iter_parent(tree_iter)
                parent = repos_model.get_value(parent_iter, 0)
                pacs_model = self.models[parent][selected]
            else:
                pacs_model = self.models[selected][_("all")]

            if self.repo_col:
                pacs_tree.remove_column(self.repo_col)
                self.repo_col = None
            if not self.inst_ver_col:
                self.inst_ver_col = pacs_tree.insert_column_with_attributes(
                    -1, _("Avaible Version"), CellRendererText(), text=4)
        pacs_tree.set_model(pacs_model)
	
	stat = (len(pacs_model), selected)
	self._statusbar(stat)

    def pacs_changed(self, widget, data=None):
	def _fork():	    
	    pac = self.database.get_by_name(name)
	    if not pac.prop_setted:
		self.database.set_pac_properties(pac)

	    #sum_buf.set_text(pac.summary)
	    self._set_pac_summary(pac)
	    file_model = file_list(pac.filelist)
	    file_tree.set_model(file_model)
	    self._statusbar()
		
        sum_txt = self.gld.get_widget("summary")
	file_tree = self.gld.get_widget("files")
        sum_buf = sum_txt.get_buffer()        
               
        model, t_iter = widget.get_selection().get_selected()
        name = model.get_value(t_iter, 2)
		
	gobject.idle_add(_fork)
	self._statusbar("Please Wait...")      
    
    def add_from_local_file(self, widget, data=None):
        dlg = local_install_fchooser_dialog(self.gld.get_widget("main_win"),
                                            self.icon)
        if dlg.run() == RESPONSE_ACCEPT:
	    self.gld.get_widget("main_win").set_sensitive(False)
            fname = dlg.get_filename()
            dlg.destroy()
        else:
            dlg.destroy()
            return
	
	self._statusbar(_("Installing %s" %fname))
        deps, conflicts = self.database.get_local_file_deps(fname)

        install = []
        remove = []
        
        for dep in deps:
	    if dep.count(">="):
		dep = dep.split(">=")[0]
            dep_pkg = self.database.get_by_name(dep)
            if dep_pkg and not dep_pkg.installed:
                install.append(dep_pkg)
            continue

        for conflict in conflicts:
            try:
                conflict_pkg = self.database.get_by_name(conflict)
		if conflict_pkg:
		    remove.append(conflict_pkg)
            except NameError:
                pass
            continue

        pacs_queues = { "add": install, "remove": remove }

        retcode = self._local_confirm(fname, pacs_queues)
        if retcode:
            i_dlg = local_install_dialog(fname, pacs_queues, self.icon)
            i_dlg.connect("destroy", self._after_local_install)
            i_dlg.run()
	self.gld.get_widget("main_win").set_sensitive(True)
	self._statusbar()

    def add_to_install_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()
        
        try:
            name = model.get_value(l_iter, 2)
        except TypeError:
            return
        
        if name in self.queues["add"]:
            return
        
        image = model.get_value(l_iter, 0)
            
        if name in self.queues["remove"]:
            self.queues["remove"].remove(name)

        self.queues["add"].append(name)
        if image == "red":
            model.set_value(l_iter, 1, STOCK_ADD)
        else:
            model.set_value(l_iter, 1, STOCK_GO_UP)
        return

    def remove_from_install_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()

        try:
            name = model.get_value(l_iter, 2)
        except TypeError:
            return
        
        if not (name in self.queues["add"]):
            return

        self.queues["add"].remove(name)
        model.set_value(l_iter, 1, None)
        return

    def add_to_remove_queue(self, widget, data=None):
        tree = self.gld.get_widget("pacs_tree")
        model, l_iter = tree.get_selection().get_selected()

        try:
            name = model.get_value(l_iter, 2)
        except TypeError:
            return
        
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

        try:
            name = model.get_value(l_iter, 2)
        except TypeError:
            return
        
        if not (name in self.queues["remove"]):
            return

        self.queues["remove"].remove(name)
        model.set_value(l_iter, 1, None)
        return
    
    def refresh_database(self, widget, data=None):
	main_window = self.gld.get_widget("main_win")
	main_window.set_sensitive(False)
	self._statusbar(_("Refreshing database..."))
        dlg = command_dialog(main_window, self.icon)
        dlg.connect("destroy", self._done_upgrade)
        dlg.run("Sy")
        return
    
    def upgrade_system(self, widget, data=None):
        to_upgrade = []
        
        for repo in self.database.values():
            for pac in repo:
                if pac.isold:
                    to_upgrade.append(pac)
                continue
            continue

        if to_upgrade:
	    self.gld.get_widget("main_win").set_sensitive(False)
	    b_list = self._blacklist( to_upgrade, 0x01)
	    if b_list:
		dlg = ignorepkg_dialog( b_list, self.icon)
		res = dlg.run()
		dlg.destroy()
		if res == RESPONSE_NO:
		    self._done(None)
		    return
	    
            confirm = self._upgrade_confirm(to_upgrade)

            if confirm:
		self._statusbar(_("Refreshing database..."))
                dlg = upgrade_dialog( self.gld.get_widget("main_win"), to_upgrade, self.icon)
                dlg.connect("destroy", self._done_upgrade)
                dlg.run()
	    else:
		self.gld.get_widget("main_win").set_sensitive(True)
        else:
	    self._statusbar(_("There isn't any packages to upgrade"))
	    self.gld.get_widget("main_win").set_sensitive(True)
        return
    
    def clear_cache(self, wid, data=None):
	main_window = self.gld.get_widget("main_win")
	main_window.set_sensitive(False)
	self._statusbar(msg=_("Clearing cache..."))
        dlg = command_dialog(main_window, self.icon)
        dlg.connect("destroy", self._done)
        dlg.run("Sc")
        return
    
    def empty_cache(self, wid, data=None):
	main_window = self.gld.get_widget("main_win")
	main_window.set_sensitive(False)
	self._statusbar(_("Emptying cache..."))
        dlg = command_dialog(main_window, self.icon)
        dlg.connect("destroy", self._done)
        dlg.run("Scc")
        return
    
    def make_package(self, widget):
        from os import chdir, geteuid, curdir
        from os.path import dirname, abspath
        
        dlg = choose_pkgbuild_dialog(self.gld.get_widget("main_win"), self.icon)
        fname = dlg.run()
        dlg.destroy()
        
        try:
            dname = dirname(fname)
        except:
	    self.gld.get_widget("main_win").set_sensitive(True)
            return

	self.gld.get_widget("main_win").set_sensitive(False)
        pwd = abspath(curdir)
        chdir(dname)

        cdlg = command_dialog(self.gld.get_widget("main_win"), self.icon)
	cdlg.connect("destroy", self._done)

        if geteuid() == 0:
            dlg = change_user_dialog(self.gld.get_widget("main_win"), self.icon)
            user = dlg.run()

            if user == "root":
                cdlg.run("makepkg --asroot -si \n", False)
            elif user == "reject":
                pass
            else:
                cdlg.run("su %s -c 'makepkg -si' \n" %user, False)
            dlg.destroy()
        else:
            cdlg.run("makepkg -si \n", False)
        chdir(pwd)
    
    def search(self, widget, data=None):	
	win = self.gld.get_widget("main_win")
	wait_cursor = Cursor(WATCH)
	        
        dlg = search_dialog(self.gld.get_widget("main_win"), self.icon)
	
	def _fork():	    
	    repos_tree = self.gld.get_widget("repos_tree")
	    repos_model = repos_tree.get_model()
	    
	    pacs = self.database.get_by_keywords(keywords)	    
	    if self.search_iter:
		repos_model.remove(self.search_iter)
	    self.search_iter = repos_model.append(None, [_("Search results for '%s'") %keywords])
	    self.models["search"] = search_list(pacs)
	    repos_tree.set_cursor_on_cell((1))
	    
	    dlg.destroy()
	    win.window.set_cursor(None)
	
        if dlg.run() == RESPONSE_ACCEPT:
            keywords = dlg.entry.get_text()
	    if keywords:
		dlg.vbox.set_sensitive(False)
		self._statusbar(_("Searching for %s..." %keywords))
		win.window.set_cursor(wait_cursor)
		dlg.window.set_cursor(wait_cursor)
		gobject.idle_add(_fork)	
	    else:
		dlg.destroy()
		error_dlg = error_dialog(None, _("You should insert at least one keyword to search for"), self.icon)
		error_dlg.run()
		error_dlg.destroy()
	else:
	    dlg.destroy()
	    
    def about(self, widget, data=None):
        dlg = about_dialog(self.icon)
        dlg.run()
        dlg.destroy()
        return
    
    def execute(self, widget=None, data=None):
        pacs_queues = { "add": [], "remove": [] }
	deps = []
        req_pacs = []
	
	# Check if pacman is old
	self._pacman_check()
	
	if self.queues['add']:
            pacs_queues['add'] = self._execute_queue_add()
	    # Check if packages are listed as ignorePkg
	    b_list = self._blacklist( pacs_queues['add'], 0x01)
	    if b_list:
		dlg = ignorepkg_dialog( b_list, self.icon)
		res = dlg.run()
		dlg.destroy()
		if res == RESPONSE_NO:
		    self._done(None)
		    return
	    
	if self.queues['remove']:
            pacs_queues['remove'], req_pacs = self._execute_queue_remove()
	    # Check if packages are listed as holdPkg
	    b_list = self._blacklist( pacs_queues['remove'], 0x02)
	    if b_list:
		dlg = holdpkg_dialog( b_list, self.icon)
		res = dlg.run()
		dlg.destroy()
		if res == RESPONSE_NO:
		    self._done(None)
		    return
	    
	if not (pacs_queues["add"] or pacs_queues["remove"]):
            self._refresh_trees_and_queues()
            return
	
	self.gld.get_widget("main_win").set_sensitive(False)
	if req_pacs:
	    dlg = warning_dialog(self.gld.get_widget("main_win"),
			     req_pacs, self.icon)
	    if dlg.run() == RESPONSE_YES:
		pacs_queues["remove"].extend(req_pacs)
		dlg.destroy()
	    else:
		#self.queues["remove"].remove(name)
		#pacs_queues["remove"].remove(pac)
		self.queues['remove'] = []
		pacs_queues['remove'] = []
		dlg.destroy()
		self._refresh_trees_and_queues()
		return

        retcode = self._confirm(pacs_queues)
	
        if retcode:
	    self._statusbar(_("Executing queued operations..."))
            dlg = do_dialog( self.gld.get_widget("main_win"), pacs_queues, self.icon)
            dlg.connect("destroy", self._refresh_trees_and_queues, pacs_queues)
            dlg.run()
        else:
            self.queues["add"] = []
            self.queues["remove"] = []
            self._refresh_trees_and_queues()
        return
    
    #------------------------- Callbacks End -----------------------------#   
    def _execute_queue_add(self):
	""" We convert names to pac (dict).
	     Then we check if there are packages that need 
	     to be installed for our selected packages (dependecies).
	"""
	queue = []
	add_queue = self.queues["add"][:]
	
	for name in add_queue:
	    pac = self.database.get_by_name(name)
            if not pac.prop_setted:
                self.database.set_pac_properties(pac)

            queue.append(pac)
	    
            if pac.dependencies:
                dep_todo_list = []
                dep_black_list = []
                deps = pac.dependencies.split(", ")
		for dep in deps:
		    if not dep in queue:
			dep_todo_list.append(dep)
		while dep_todo_list:
		    dep = dep_todo_list.pop(0)
		    if dep.count(">="):
			dep = dep.split(">=")[0]
		    if dep.count('<'):
			dep = dep.split('<')[0]
		    if dep.count("="):
			dep = dep.split("=")[0]
		    if not (dep in self.queues["add"]):
			done, to_do = self._execute_dep_check(dep, "dep")
			if done and not done in queue:
			    done.flag = 11
			    queue.append(done)
			for add in to_do:
			    if not add in dep_black_list:
				dep_todo_list.append(add)
				dep_black_list.append(add)
	return queue
	
    def _execute_queue_remove(self):
	queue = []
	req_pacs = []
	remove_queue = self.queues["remove"][:]
	
	for name in remove_queue:
            pac = self.database.get_by_name(name)
            if not pac.prop_setted:
                self.database.set_pac_properties(pac)

	    queue.append(pac)
            if pac.req_by:
                req_todo_list = []
                req_black_list = []
                for req in pac.req_by.split(", "):
                    if not (req in self.queues["remove"]):
                        req_todo_list.append(req)
                while req_todo_list:
                    req = req_todo_list.pop(0)
                    if not (req in self.queues["remove"]):
                        done, to_do = self._execute_dep_check(req, "req")
                        if done and not done in req_pacs:
                            req_pacs.append(done)
                        for add in to_do:
                            if not add in req_black_list:
                                req_todo_list.append(add)
                                req_black_list.append(add)
	return queue, req_pacs
				
    def _execute_dep_check(self, to_check, flag):
	to_do = []
	try:
	    pac = self.database.get_by_name(to_check)
	except NameError:
	    dlg = error_dialog(self.gld.get_widget("main_win"),
	    _("%(dep)s is not in the database. %(dep)s is required by %(pkg)s.\nThis maybe either an error in %(pkg)s packaging or a gtkpacman's bug.\nIf you think it's the first, contact the %(pkg)s maintainer, else fill a bug report for gtkpacman, please.") %{'dep': dep, "pkg": name}, self.icon)
	    dlg.run()
	    dlg.destroy()
	    pacs_queues["add"].remove(pac)
	    self.queues["add"].remove(name)
	    return
	try:
	    if not pac.prop_setted:
		self.database.set_pac_properties(pac)
	except:
	    return pac, to_do
	
	if flag == "req":
	    for req in pac.req_by.split(", "):
		if len(req) >= 1:
		    to_do.append(req)
	else:
	    if not pac.installed:
		for dep in pac.dependencies.split(", "):
		    if len(dep) >= 1:
			to_do.append(dep)
		    else:
			pac = None
		return pac, to_do
	    pac = None
    
	return pac, to_do
				
    def _confirm(self, pacs_queues):
        dlg = confirm_dialog(self.gld.get_widget("main_win"), pacs_queues, self.icon)
        retcode = dlg.run()
        return retcode   
	
    def _after_local_install(self, wid, data=None):
        self.database.refresh()
        self.models["foreigners"] = installed_list(self.database["foreigners"])
	self.gld.get_widget("main_win").set_sensitive(True)

	self._statusbar()

    def _local_confirm(self, fname, pacs_queue):
        dlg = local_confirm_dialog(self.gld.get_widget("main_win"),
                                   fname, pacs_queue, self.icon)
        if dlg.run():
            retcode = True
        else:
            retcode = False
        return retcode

    def _upgrade_confirm(self, to_upgrade):
        dlg = upgrade_confirm_dialog(self.gld.get_widget("main_win"),
                                     to_upgrade, self.icon)
        retcode = dlg.run()
        return retcode
    
    def _blacklist(self, pacs, key=None):
	""" Here we check if packages are not in hold or ignore list.
	    If they are then we return them.
	"""
	blacklist = []
	if pacs and key == 0x01:
	    for bp in self.database.ignorePkg:
		for p in pacs:
		    if p.name == bp:
			blacklist.append(p.name)
	elif pacs and key == 0x02:
	    for bp in self.database.holdPkg:
		for p in pacs:
		    if p.name == bp:
			blacklist.append(p.name)
	else:
	    return None
	
	return blacklist

    def _done_upgrade(self, widget, data=None):
        self.database.refresh()
        self._refresh_repos_tree()
        self._setup_pacs_models()
	self._statusbar(_("Updating compleated"))
	self.gld.get_widget("main_win").set_sensitive(True)
	
    def _done(self, widget, data=None):
	self.gld.get_widget("main_win").set_sensitive(True)
	self._statusbar()
	
    def quit(self, widget, data=None):
        main_quit()
        return
    def _pacman_check(self):
	"""Check if pacman is old, if true than update pacman
	"""
	# TODO ************************************************
	# I'm not sure if this will be default action for when checking if pacman is old.
	for pac in self.database['core']:
	    # 
	    if pac.name == 'pacman' and pac.installed == False:
		dlg = info_dialog( self.gld.get_widget('main_win'), "Warning:: Pacman is not installed,\n This isn't right, REPORT IT PLEASE", self.icon)
		dlg.run()
		dlg.destroy()
	    if pac.name == 'pacman' and pac.isold == True:
		#self.queues['add'].insert(0, pac)
		dlg = info_dialog( self.gld.get_widget('main_win'), 'Newer Pacman version is avaible', self.icon)
		dlg.run()
		dlg.destroy()
		
    def _statusbar(self, msg=None):
	stat_bar = self.gld.get_widget("statusbar")

	if type(msg) == type(()):
	    str = _("%s packages in [ %s ]") %(msg[0], msg[1])
	elif msg == None:
	    str =  _("Done")
	else:
	    str = "%s " %msg
	stat_bar.push(-1, str)
    
    def _set_pac_summary(self, pac):
        sum_txt = self.gld.get_widget("summary")
        file_tree = self.gld.get_widget("files")
        
        #text_buffer = TextBuffer()
        #text_buffer.set_text(pac.summary)
        #sum_txt.set_buffer(text_buffer)
        
        text_buffer = TextBuffer()
        tag_table = text_buffer.get_tag_table()
        heading_tag = TextTag("heading")
        heading_tag.set_property("weight", pango.WEIGHT_BOLD)
        heading_tag.set_property("foreground", "grey")
	
	description_tag = TextTag("desc_tag")
        description_tag.set_property("indent", -15)
        
        center_tag = TextTag("center")
        #center_tag.set_property("indent", 800)
        center_tag.set_property("foreground", "blue")
        #center_tag.set_property("left-margin", 90)
        tag_table.add(heading_tag)
        tag_table.add(center_tag)
	tag_table.add(description_tag)
        
        iter = text_buffer.get_start_iter()
        #iter, eob = text_buffer.get_bounds()
        
        if pac.installed:
            text_buffer.insert_with_tags_by_name(iter, "Description\n", 'heading')
            text_buffer.insert_with_tags_by_name(iter, pac.summary[0] + "\n", "desc_tag")
	    
	    text_buffer.insert_with_tags_by_name(iter, "Install Date\n", 'heading')
            text_buffer.insert(iter, pac.summary[5] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Size\n", 'heading')
            text_buffer.insert(iter, pac.summary[6] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Install Reason\n", 'heading')
            text_buffer.insert(iter, pac.summary[7] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Required By\n", 'heading')
            text_buffer.insert_with_tags_by_name(iter, pac.summary[2] + "\n", "desc_tag")
            
            text_buffer.insert_with_tags_by_name(iter, "Depends On\n", 'heading')
            text_buffer.insert_with_tags_by_name(iter, pac.summary[1] + "\n", "desc_tag")
            
            text_buffer.insert_with_tags_by_name(iter, "Packager\n", 'heading')
            text_buffer.insert_with_tags_by_name(iter, pac.summary[3] + "\n", "desc_tag")
            
            text_buffer.insert_with_tags_by_name(iter, "Build Date\n", 'heading')
            text_buffer.insert(iter, pac.summary[4])
            
            sum_txt.set_buffer(text_buffer)
    
            file_model = file_list(pac.filelist)
            file_tree.set_model(file_model)
        else:            
            text_buffer.insert_with_tags_by_name(iter, "Description\n", "heading")
            text_buffer.insert_with_tags_by_name(iter, pac.summary[0] + "\n", "desc_tag")
	    
	    text_buffer.insert_with_tags_by_name(iter, "Size (compressed)\n", "heading")
            text_buffer.insert(iter, pac.summary[2] + "\n")
            #text_buffer.insert_with_tags_by_name(iter, pac.summary[2], "center")
            
            text_buffer.insert_with_tags_by_name(iter, "Depends On\n", "heading")
            text_buffer.insert_with_tags_by_name(iter, pac.summary[1], "desc_tag")
            
            sum_txt.set_buffer(text_buffer)
