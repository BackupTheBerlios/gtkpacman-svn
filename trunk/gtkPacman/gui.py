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

import gettext, gobject, pango, webbrowser

from gtk import main, main_quit, TreeStore, TreeView, ListStore, Button
from gtk import CellRendererText, CellRendererPixbuf, ScrolledWindow
from gtk import STOCK_ADD, STOCK_GO_UP, STOCK_REMOVE, STOCK_CLOSE
from gtk import RESPONSE_YES, RESPONSE_ACCEPT, RESPONSE_OK, RESPONSE_NO, RESPONSE_REJECT
from gtk import TextBuffer, TextTag, TEXT_WINDOW_TEXT, TEXT_WINDOW_WIDGET
from gtk.gdk import pixbuf_new_from_file, Cursor, WATCH, HAND2, XTERM, BUTTON_RELEASE
from gtk.glade import XML

from dialogs import about_dialog, warning_dialog, do_dialog
from dialogs import search_dialog, upgrade_dialog
from dialogs import local_install_dialog, password_dialog
from dialogs import local_install_fchooser_dialog
from dialogs import command_dialog, error_dialog, ignorepkg_dialog
from dialogs import holdpkg_dialog, choose_pkgbuild_dialog, change_user_dialog

from models import installed_list, all_list, explicitly_list, search_list, file_list, orphan_list

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
                  "make_pkg":       self.make_package,
                  "sum_txt_on_motion": self.sum_txt_on_motion}
        self.gld.signal_autoconnect(h_dict)

        self.uid = uid
        self.fname = fname
        self.icon = icon
        self.database = database
        self.queues = {"add": [], "remove": []}
        self.search_iter = None

        #Setup secondary gui elements
        self._setup_popup_menu(fname)
        self._setup_repos_tree()
        self._setup_pacs_models()
        self._setup_combobox()
        self._setup_pacs_tree()
        self._setup_files_tree()
        
        self._setup_log()
        self._statusbar('Ready for your command')
        #Check pacman version
        self._pacman_ver_check()

        #Deactivate some widgets
        self.gld.get_widget("makepkg").set_sensitive(False)
    
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
        repos_tree = self.gld.get_widget("repos_tree")
        
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

        sort_id = 0
        for col in pacs_tree.get_columns():
            col.set_reorderable(True)
            col.set_sort_column_id(sort_id)
            col.set_clickable(True)
            col.set_resizable(True)
            sort_id += 1            
        col.set_visible(False)
        
        col_4 = pacs_tree.get_column(4)
        col_4.set_max_width(105)
        # Select first repo in repos_tree
        repos_tree.set_cursor_on_cell(0)

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

        try:
            self.models[_("foreigners")] = installed_list(self.database["foreigners"])
        except KeyError:
            self.database["foreigners"] = []
            self.models[_("foreigners")] = installed_list(self.database["foreigners"])
            
        for repo in self.database.keys():
            if repo == _("foreigners") or repo == "local":
                continue
            
            self.models[repo] = {}

            all_mod = all_list(self.database[repo])
            inst_mod = installed_list(self.database[repo])

            self.models[repo][_("all")] = all_mod
            if repo != 'local':
                self.models[repo][_("installed")] = inst_mod
        
        return
    
    def _setup_combobox(self):
        
        combo_list = ListStore(str)
        combo_box = self.gld.get_widget("combo_box_options")
        combo_box.set_model(combo_list)
        
        combo_box.append_text("all")
        combo_box.append_text("installed")
        combo_box.append_text("explicitly installed")
        
        combo_box.set_active(0)
        
        combo_box.connect("changed", self.combobox_options_changed)
        
    def _setup_log(self):
        log_text_view = self.gld.get_widget("log")
        text_buffer = TextBuffer()
        iter = text_buffer.get_start_iter()
        log_file = self.database.log.values()[0]
        
        while log_file:
            text_buffer.insert(iter, log_file.pop())
        log_text_view.set_buffer(text_buffer)

    def _make_repos_model (self):
        repos_model = TreeStore(str)
        repos = sorted( self.database.repos.keys() )
        
        for repo in repos:
            if repo == "foreigners" or repo == "local":
                continue
            repo_it = repos_model.append(None, [repo])
        
        repos_model.append(None, [_("foreigners")])   
        repos_model.append(None, [_("orphans")])

        return repos_model 
    
    #------------------------ Refresh: database, models, trees, repos ------------#
    def _refresh_trees_and_queues(self, widget=None, pacs_queues=None):
        selected_pac_before = str()
        selected_pac_after = str()
        selected_pac_path = None
        selected_repo_path = None
        
        repos_tree = self.gld.get_widget("repos_tree")
        pacs_tree = self.gld.get_widget("pacs_tree")
        
        repos_model, repo_iter = repos_tree.get_selection().get_selected()
        # Need to be sure that repository was selected before fetching it's name
        if repo_iter:
            selected_repo_path = repos_model.get_path(repo_iter)
            selected_repo = repos_model.get_value(repo_iter, 0)
        
        pacs_model, pac_iter = pacs_tree.get_selection().get_selected()
        # Need to be sure that package was selected before fetching packages name
        if pac_iter:
            selected_pac_before = pacs_model.get_value(pac_iter, 2)
            selected_pac_path = pacs_model.get_path(pac_iter)
        
        # Refresh database, packages models, repositories models
        self.database.refresh()
        self._setup_pacs_models()
        repos_tree.set_model(self._make_repos_model())
        
        # Check if repo was selected
        if type(selected_repo_path) == tuple:
            repos_tree.set_cursor(selected_repo_path)
            pacs_model = pacs_tree.get_model()
        else:
            repos_tree.set_cursor_on_cell(0)

        # Check if selected pac path is tuple, otherwise it wasn't selected and we skip this moment
        if type(selected_pac_path) == tuple:
            try:
                pac_iter = pacs_model.get_iter(selected_pac_path)
                selected_pac_after = pacs_model.get_value(pac_iter, 2)
            except ValueError:
                pass
        
        # Compare pacs after refreshing, if match then select both repository and package
        if (selected_pac_before and selected_pac_before == selected_pac_after and selected_repo != 'orphans'):
            pacs_tree.scroll_to_cell(selected_pac_path)
            pacs_tree.set_cursor(selected_pac_path)
        else:
            summary_buffer = self.gld.get_widget("summary").get_buffer()
            file_tree = self.gld.get_widget("files")
            summary_buffer.set_text('')
            file_model = file_tree.get_model()
            if file_model:
                file_model.clear()
                file_tree.set_model(file_model)
            
        del(pacs_queues)
        self.queues["add"] = []
        self.queues["remove"] = []
        self._setup_log()
        self._pacman_ver_check()
        self._statusbar()
        self.gld.get_widget("main_win").set_sensitive(True)
        
    #----------------------------- Refresh End ---------------------------#
    
    #----------------------------- Callbacks ------------------------------#
    def show_popup(self, widget, event, data=None):
        if event.button == 3:
            self.popup.popup(None, None, None, event.button, event.time)
        else:
            self.popup.popdown()
            
    def combobox_options_changed(self, widget, data=None):
        
        repos_tree = self.gld.get_widget("repos_tree")
        pacs_tree = self.gld.get_widget("pacs_tree")
        combo_box_options = self.gld.get_widget("combo_box_options")
        
        repos_model, tree_iter = repos_tree.get_selection().get_selected()
        selected_repo = repos_model.get_value(tree_iter, 0)
        selected_option = combo_box_options.get_active_text()
        
        if selected_option == 'explicitly installed':
            try:
                pacs_model = self.models[ selected_repo ][ selected_option ]
            except KeyError:
                self.database.set_reason(selected_repo)
                self.models[ selected_repo ]['explicitly installed' ] = explicitly_list(self.database[ selected_repo ])
            
        pacs_model = self.models[ selected_repo ][ selected_option ]
        pacs_tree.set_model(pacs_model)
        
        stat = (len(pacs_model), selected_repo, self.database.repos.get( selected_repo ))
        self._statusbar(stat)
        
    def repo_changed(self, widget, data=None):
        def _setup_status(pacs_model, ext_msg=True):
            # ext_msg = extended message
            pacs_tree.set_model(pacs_model)
            # pass more info to statusbar if repo isn't: orphans, foreigners or Search...
            if ext_msg:
                stat = (len(pacs_model), selected_repo, self.database.repos.get( selected_repo ))
                self._statusbar(stat)
            else:
                stat = (len(pacs_model), selected_repo)
                self._statusbar(stat)
            
        def _setup_orphans_fork():
            self.database.set_orphans()
            self.models['orphans'] = orphan_list( self.database['local'] )
            parent_iter = repos_model.iter_parent(tree_iter)
            
            _setup_status( self.models['orphans'], False )
            main_win.window.set_cursor(None)
        
        repos_tree = self.gld.get_widget("repos_tree")
        pacs_tree = self.gld.get_widget("pacs_tree")
        combo_box_options = self.gld.get_widget("combo_box_options")
        
        # Hide last column 'Repo' if it's visible
        col_5 = pacs_tree.get_column(5)
        col_5.set_visible(False)

        repos_model, tree_iter = repos_tree.get_selection().get_selected()
        # Need to be sure that repo was selected
        if tree_iter:
            selected_repo = repos_model.get_value(tree_iter, 0)
        # If it wasn't than we select first repo available and return
        else:
            repos_tree.set_cursor_on_cell(0)
            return
        
        # When clicking on repo we unselect any selected pac and clear summary and files
        pacs_tree.get_selection().unselect_all()
        summary_buffer = self.gld.get_widget("summary").get_buffer()
        file_tree = self.gld.get_widget("files")
        summary_buffer.set_text('')
        file_model = file_tree.get_model()
        if file_model:
            file_model.clear()
            file_tree.set_model(file_model)
        
        # Fetch orphans packages
        if selected_repo == 'orphans':
            combo_box_options.set_sensitive(False)
            col_5.set_visible(True)
            try:
                _setup_status( self.models['orphans'], False )
            except KeyError:
                main_win = self.gld.get_widget("main_win")
                main_win.window.set_cursor(Cursor(WATCH))
                self._statusbar('Please wait...')
                gobject.idle_add(_setup_orphans_fork)
        
        # If selected repo is: foreigners, orphans or search then we deactivate combo_box_options
        elif selected_repo == 'foreigners' or selected_repo.startswith('Search'):
            combo_box_options.set_sensitive(False)
                    
            # Fetch search model
            if selected_repo.startswith('Search'):
                col_5.set_visible(True)
                pacs_model = self.models["search"]
                
            # Jump in if selected repo is foreigners
            else:
                pacs_model = self.models[ selected_repo ]
                pacs_tree.set_model(pacs_model)
                
            _setup_status(pacs_model, False)
            
        # Otherwise we check selected option from combo_box_options and 
        # fetch model appropriate to selected option
        else:
            combo_box_options.set_sensitive(True)
            selected_option = combo_box_options.get_active_text()
            
            if selected_option == 'explicitly installed':
                try:
                    pacs_model = self.models[ selected_repo ][ selected_option ]
                except KeyError:
                    self.database.set_reason(selected_repo)
                    self.models[ selected_repo ][ 'explicitly installed' ] = explicitly_list(self.database[ selected_repo ])
            
            pacs_model = self.models[ selected_repo ][ selected_option ]
            _setup_status(pacs_model)

    def pacs_changed(self, widget, data=None):
        def _fork():        
            pac = self.database.get_by_name(name)
            if not pac.prop_setted:
                self.database.set_pac_properties(pac)

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
        main_win = self.gld.get_widget("main_win")
        dlg = local_install_fchooser_dialog(main_win, self.icon)
        if dlg.run() == RESPONSE_ACCEPT:
            main_win.set_sensitive(False)
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

        local_install_dlg = local_install_dialog( main_win, self.icon, pacs_queues, fname )
        local_install_dlg.connect("destroy", self._refresh_trees_and_queues)
        
        retcode = local_install_dlg.run()        
        if retcode == RESPONSE_YES:
            self._statusbar(_("Installing..."))
            local_install_dlg.set_sensitive(False)
            if self._passwd_dlg_init(local_install_dlg):
                    local_install_dlg.install()
                    local_install_dlg.set_sensitive(True)
            else:
                local_install_dlg.destroy()
                self._statusbar(_("Installation canceled"))
        else:
            local_install_dlg.destroy()

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
        command_dlg = command_dialog(main_window, self.icon)
        command_dlg.connect("destroy", self._refresh_trees_and_queues)
        
        if self._passwd_dlg_init(command_dlg):
            command_dlg.install('Sy')
        else:
            command_dlg.destroy()

        #self.gld.get_widget("repos_tree").set_cursor_on_cell(0)
    
    def upgrade_system(self, widget, data=None):
        to_upgrade = []
        
        for repo in self.database.values():
            for pac in repo:
                if pac.isold:
                    to_upgrade.append(pac)
                continue
            continue
        
        # Jump in if there are packages to upgrade
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
            
            upgrade_dlg = upgrade_dialog( self.gld.get_widget("main_win"), self.icon, to_upgrade)
            upgrade_dlg.connect("destroy", self._refresh_trees_and_queues)
        
            resp = upgrade_dlg.run()
            if resp == RESPONSE_YES:
                self._statusbar(_("Refreshing database..."))
                upgrade_dlg.set_sensitive(False)
                if self._passwd_dlg_init(upgrade_dlg):
                    upgrade_dlg.install()
                    upgrade_dlg.set_sensitive(True)
                else:
                    upgrade_dlg.destroy()
                    self._statusbar(_("Upgrade canceled"))
                    self.gld.get_widget("main_win").set_sensitive(True)
                    
            elif resp == RESPONSE_NO:
                upgrade_dlg.destroy()
                self._statusbar(_("Upgrade canceled"))
                self.gld.get_widget("main_win").set_sensitive(True)
            else:
                print 'else'

        # Else nothing to upgrade
        else:
            self._statusbar(_("There are no packages to upgrade"))
            self.gld.get_widget("main_win").set_sensitive(True)
        return
    
    def clear_cache(self, wid, data=None):
        main_window = self.gld.get_widget("main_win")
        main_window.set_sensitive(False)
        self._statusbar(msg=_("Clearing cache..."))
        command_dlg = command_dialog(main_window, self.icon)
        command_dlg.connect("destroy", self._done)
        
        if self._passwd_dlg_init(command_dlg):
            command_dlg.install('Sc')
        else:
            command_dlg.destroy()
        
    def empty_cache(self, wid, data=None):
        main_window = self.gld.get_widget("main_win")
        main_window.set_sensitive(False)
        self._statusbar(_("Emptying cache..."))
        command_dlg = command_dialog(main_window, self.icon)
        command_dlg.connect("destroy", self._done)
 
        if self._passwd_dlg_init(command_dlg):
            command_dlg.install('Scc')
        else:
            command_dlg.destroy()            
    
    def make_package(self, widget):
        from os import chdir, geteuid, curdir
        from os.path import dirname, abspath
        from pwd import getpwuid
        
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

        command_dlg = command_dialog(self.gld.get_widget("main_win"), self.icon)
        command_dlg.connect("destroy", self._done)
        
        
        if geteuid() == 0:
            dlg = change_user_dialog(self.gld.get_widget("main_win"), self.icon)
            user = dlg.run()
            dlg.destroy()

            if user == "root":
                command_dlg.install("makepkg --asroot -si \n", False)
            elif user == "reject":
                pass
            else:
                command_dlg.install("su %s -c 'makepkg -si' \n" %user, False)
            #command_dlg.destroy()
        else:
            if self._passwd_dlg_init(command_dlg):
                usr_name = getpwuid(geteuid())[0]
                command_dlg.install("su %s -c 'makepkg -si' \n" %usr_name, False)
            else:
                command_dlg.destroy()
            #command_dlg.install("makepkg -s \n", False)
        #command_dlg.destroy()
        chdir(pwd)
    
    def search(self, widget, data=None):        
        main_win = self.gld.get_widget("main_win")
                
        dlg = search_dialog(main_win, self.icon)
        
        def _fork():
            repos_tree = self.gld.get_widget("repos_tree")
            repos_model = repos_tree.get_model()
            
            pacs = self.database.get_by_keywords(keywords.lower())
            if self.search_iter:
                repos_model.remove(self.search_iter)
            self.search_iter = repos_model.append(None, [_("Search for '%s'") %keywords])
            self.models["search"] = search_list(pacs)
            path = repos_model.get_path(self.search_iter)
            repos_tree.set_cursor_on_cell(path)

            dlg.destroy()
            main_win.window.set_cursor(None)
        
        if dlg.run() == RESPONSE_ACCEPT:
            keywords = dlg.entry.get_text()
            if keywords:
                dlg.vbox.set_sensitive(False)
                self._statusbar(_("Searching for %s..." %keywords))
                main_win.window.set_cursor(Cursor(WATCH))
                dlg.window.set_cursor(Cursor(WATCH))
                gobject.idle_add(_fork)
            else:
                dlg.destroy()
                error_dlg = error_dialog(None, _("You should insert at least one keyword to search for"), self.icon)
                error_dlg.run()
                error_dlg.destroy()
        else:
            dlg.destroy()
            
    def about(self, widget, data=None):
        dlg = about_dialog(self.gld.get_widget("main_win"), self.icon)
        dlg.run()
        dlg.destroy()
        return
    
    def quit(self, widget, data=None):
        main_quit()
        return
    
    def sum_txt_on_motion(self, widget, event, data=None):
        """ Change cursor when hovering over hyperlink
        """        
        x, y = widget.window_to_buffer_coords(TEXT_WINDOW_WIDGET,
        int(event.x), int(event.y))
        buffer = widget.get_buffer()
        iter = widget.get_iter_at_location(x, y)
        tags = iter.get_tags()
        
        for tag in tags:
            url = tag.get_data("url")
            if url:
                widget.get_window(TEXT_WINDOW_TEXT).set_cursor(Cursor(HAND2))
            else:
                widget.get_window(TEXT_WINDOW_TEXT).set_cursor(Cursor(XTERM))
                
        return False
    
    def execute(self, widget=None, data=None):
        pacs_queues = { "add": [], "remove": [] }
        deps = []
        req_pacs = []
        
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
                self.queues['remove'] = []
                pacs_queues['remove'] = []
                dlg.destroy()
                self._refresh_trees_and_queues()
                return

        # Open new dialog and execute commands ie. install/remove packages
        do_dlg = do_dialog( self.gld.get_widget("main_win"), self.icon, pacs_queues)
        do_dlg.connect("destroy", self._refresh_trees_and_queues)
        
        resp = do_dlg.run()
        if resp == RESPONSE_YES:
            self._statusbar(_("Executing queued operations..."))
            do_dlg.set_sensitive(False)
            if self._passwd_dlg_init(do_dlg):
                do_dlg.install()
                do_dlg.set_sensitive(True)
            # User clicked cancel
            else:
                do_dlg.destroy()
                self.queues["add"] = []
                self.queues["remove"] = []
                self._statusbar(_("Upgrade canceled"))
                self.gld.get_widget("main_win").set_sensitive(True)
                
        elif resp == RESPONSE_NO:
            do_dlg.destroy()
            self.queues["add"] = []
            self.queues["remove"] = []
            self._statusbar(_("Upgrade canceled"))
            self.gld.get_widget("main_win").set_sensitive(True)
    
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
                        if not done:
                            continue
                        #if done and not done in queue:
                        if done and not done in queue and not done.installed:
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

        pac = self.database.get_by_name(to_check)
        if not pac:
            dlg = error_dialog(self.gld.get_widget("main_win"),
            _("%(pkg)s is not in the database. %(pkg)s is required by one of your package(s).\n \
            This maybe either an error in %(pkg)s packaging or a gtkpacman's bug.\n \
            If you think it's the first, contact the %(pkg)s maintainer, else fill a bug report for gtkpacman, please.") %{"pkg": to_check}, self.icon)
            dlg.run()
            dlg.destroy()
            #self.queues["add"].pop(0)
            #self.queues["add"].remove(name)
            return
        
        if not pac.prop_setted:
            self.database.set_pac_properties(pac)
        else:
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
                                
    def _passwd_dlg_init(self, dlg):
        """ We check if gtkpacman was started by root. 
            If not then we run password_dialog
        """
        warning_ison = False
        # Jump in if program was not started by root
        if self.uid:
            dlg.run_su()
            passwd_dlg = password_dialog(self.gld.get_widget("main_win"), self.icon)
            # When password is less then 1 we show 'error' message. 
            # Until passwd is less than one and unverified we keep password_dialog runing.
            while passwd_dlg.run() == RESPONSE_ACCEPT:
                user_passwd = passwd_dlg.password_entry.get_text()
                if not len(user_passwd) > 0:
                    # We don't want to show same message everytime user click on OK button
                    if not warning_ison:
                        passwd_dlg.show_warning()
                        warning_ison = True
                # Return with valid password
                else:
                    passwd_dlg.destroy()
                    dlg.run_login(user_passwd)
                    del user_passwd
                    return True
            # Destroy dialog and return False when user click on Cancel
            passwd_dlg.destroy()
            return False
        # We return if program was started by root
        else:
            return True
    
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
        
    def _done(self, widget, data=None):
        self.gld.get_widget("main_win").set_sensitive(True)
        self._statusbar()
        
    def _pacman_ver_check(self):
        """Check pacman version.
        """
        pacman_ver = self.gld.get_widget('pacman_ver_status')
        ver_inst = self.gld.get_widget('ver_inst_label')
        ver_avail = self.gld.get_widget('ver_avail_label')
        
        for pac in self.database['core']:
            # Print pacmans installed and avaible version
            if pac.name == 'pacman':
                if pac.isold == False:
                    pacman_ver.hide()
                    return
                elif (pac.name == 'pacman' and ( pac.isold == True and pac.installed == True )):
                    pacman_ver.show()
                    ver_inst.set_text(pac.inst_ver)
                    ver_avail.set_text(pac.version)
                    return
                # If pacman is found but 'installed == False' then we print warning
                else:
                    pacman_ver.show()
                    ver_inst.set_text('WARNING')
                    ver_avail.set_text('WARNING')
                    print "?? WARNING: Found pacman but it's not installed"
                    return
                
        # If can't find pacman in core repo then print warning
        pacman_ver.show()
        ver_inst.set_text('WARNING')
        ver_avail.set_text('WARNING')
        print "!! WARNING: Can't find pacman in 'core' repo"

    def _statusbar(self, msg=None):
        stat_bar = self.gld.get_widget("statusbar")

        if type(msg) == tuple and len(msg) == 3:
            str = _("%s packages in [ %s ] - last synchronized [ %s ]") %(msg[0], msg[1], msg[2])
        elif type(msg) == tuple and len(msg) == 2:
            str = _("%s packages in [ %s ]") %(msg[0], msg[1])
        elif msg == None:
            str =  _("Done")
        else:
            str = "%s " %msg
        stat_bar.push(-1, str)
    
    def _set_pac_summary(self, pac):
        sum_txt = self.gld.get_widget("summary")
        file_tree = self.gld.get_widget("files")

        def list_tag(tag, widget, event, iter):
            if event.type == BUTTON_RELEASE:
                buff = widget.get_buffer()
                url = tag.get_data("url")
                if url:
                    webbrowser.open_new_tab(url)
        
        text_buffer = TextBuffer()
        tag_table = text_buffer.get_tag_table()
        heading_tag = TextTag("heading")
        heading_tag.set_property("weight", pango.WEIGHT_BOLD)
        heading_tag.set_property("foreground", "grey")

        link_tag = TextTag('link')
        link_tag.set_property("foreground", 'brown')
        link_tag.set_property('underline', pango.UNDERLINE_SINGLE)
        link_tag.set_data("url", pac.url)
        link_tag.connect("event", list_tag)
        
        center_tag = TextTag("center")
        #center_tag.set_property("indent", 800)
        center_tag.set_property("foreground", "blue")
        #center_tag.set_property("left-margin", 90)
        tag_table.add(heading_tag)
        tag_table.add(center_tag)
        tag_table.add(link_tag)
        
        iter = text_buffer.get_start_iter()
        
        if pac.installed:
            text_buffer.insert_with_tags_by_name(iter, "Description\n", 'heading')
            text_buffer.insert(iter, pac.description[0] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Size\n", 'heading')
            text_buffer.insert(iter, pac.size + "\n")

            text_buffer.insert_with_tags_by_name(iter, "URL\n", 'heading')
            text_buffer.insert_with_tags_by_name(iter, pac.url, 'link')
            text_buffer.insert(iter, "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Install Date\n", 'heading')
            text_buffer.insert(iter, pac.dates[0] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Install Reason\n", 'heading')
            text_buffer.insert(iter, pac.explicitly[0] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Required By\n", 'heading')
            text_buffer.insert(iter, pac.req_by + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Depends On\n", 'heading')
            text_buffer.insert(iter, pac.dependencies + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Packager\n", 'heading')
            text_buffer.insert(iter, pac.description[1] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Build Date\n", 'heading')
            text_buffer.insert(iter, pac.dates[1])

            sum_txt.set_buffer(text_buffer)
    
        else:            
            text_buffer.insert_with_tags_by_name(iter, "Description\n", "heading")
            text_buffer.insert(iter, pac.description[0] + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Size (compressed)\n", "heading")
            text_buffer.insert(iter, pac.size + "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "URL\n", 'heading')
            text_buffer.insert_with_tags_by_name(iter, pac.url, 'link')
            text_buffer.insert(iter, "\n")
            
            text_buffer.insert_with_tags_by_name(iter, "Depends On\n", "heading")
            text_buffer.insert(iter, pac.dependencies, )
            
            sum_txt.set_buffer(text_buffer)
