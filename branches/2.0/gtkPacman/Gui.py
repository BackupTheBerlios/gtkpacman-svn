import gtk, gtk.glade, thread, time

from Pacman import *
from Models import *

class gui:

    def __init__(self, fname, icons):

        self.gld = gtk.glade.XML(fname, 'main_win', 'gtkpacman')
        hands = { 'hide_win' : self.hide,
                  'quit' : self.quit,
                  'on_preferences' : self.preferences,
                  'on_about' : self.about,
                  'sync' : self.sync,
                  'upgrade' : self.upgrade,
                  'add' : self.add,
                  'refresh' : self.refresh,
                  'remove' : self.remove,
                  'toolbar': self.toolbar,
                  'pack_infos' : self.pack_infos,
                  'old_packs' : self.old_packs }
        
        self.gld.signal_autoconnect(hands)

        self.pacman = pacman(self)
        self.db = self.pacman.db
        self.db_ready = False
        self.old_model = gtk.ListStore(str, str, str, str)

        self._setup_trees()
        self._setup_dep_and_req_by_trees()
        self._setup_icons(icons)
        
        icon = gtk.gdk.pixbuf_new_from_file(icons["pacman"])
        self.gld.get_widget("main_win").set_icon(icon)

        self.stat_bar = self.gld.get_widget("statusbar")
        self.cont_id = self.stat_bar.get_context_id("statusbar")

        self.prog_bar = gtk.ProgressBar()
        self.stat_bar.pack_end(self.prog_bar, False, True, 0)


    def _do_pulse(self):
        while self.pulse:
            gtk.threads_enter()
            self.prog_bar.pulse()
            gtk.threads_leave()
            time.sleep(0.1)
        return
    
    def _get_selected_pac(self, tree):
        (model, treeiter) = tree.get_selection().get_selected()
        name = model.get_value(treeiter, 1)
        pac = self.db.get_by_name(name)
        return pac
            
    def _init_db(self):

        gtk.threads_enter()
        self.prog_bar.show()
        gtk.threads_leave()
               
        self.db.setup_pacs(self._set_progress, self._reset_progress)
        self.db_ready = True
        
        gtk.threads_enter()
        self.prog_bar.hide()
        self.stat_bar.pop(self.cont_id)
        self.stat_bar.push(self.cont_id, "Done")
        gtk.threads_leave()
        
    def _reset_progress(self, repo):
        gtk.threads_enter()
        self.prog_bar.set_fraction(0.0)
        self.stat_bar.pop(self.cont_id)
        self.stat_bar.push(self.cont_id, "Setting %s packages list" %repo)
        self.trees[repo].set_model(pac_model(repo, self.db,
                                             self.old_model))
        gtk.threads_leave()
        return
        
    def _set_desc(self, pac):
        desc = pac[0][2]
        summ_txt = self.gld.get_widget("summary_txt").get_buffer()
        summ_txt.set_text(desc)
        return

    def _set_flist(self, pac):
        flist_txt = self.gld.get_widget("filelist_txt").get_buffer()
        flist_txt.set_text("")
        
        if len(pac) < 7:
            flist_txt.set_text("%s is not installed" %pac[0][0])
        else:
            for file in pac[3]:
                flist_txt.insert(flist_txt.get_end_iter(), "%s\n" %file)
                continue
        return

    def _set_old_model(self):

        import time
        
        while not self.db_ready:
            time.sleep(1.0)

        gtk.threads_enter()
        self.trees["old"].set_model(self.old_model)
        gtk.threads_leave()

    def _set_progress(self, fraction, repo, pack_name):

        gtk.threads_enter()
        curr_fraction = self.prog_bar.get_fraction()
        gtk.threads_leave()
        
        new_fraction = curr_fraction + fraction
        if new_fraction >= 1.0:
            new_fraction = 1.0

        gtk.threads_enter()
        self.stat_bar.pop(self.cont_id)
        self.stat_bar.push(
            self.cont_id,
            "Processing %s repo - package: %s" %(repo, pack_name)
            )
        self.prog_bar.set_fraction(new_fraction)
        gtk.threads_leave()
        return
            
    
    def _setup_columns(self, tree):

        tree.insert_column_with_attributes(-1,
                                           "",
                                           gtk.CellRendererPixbuf(),
                                           stock_id = 0)
        tree.insert_column_with_attributes(-1,
                                           "Package",
                                           gtk.CellRendererText(),
                                           text = 1)
        tree.insert_column_with_attributes(-1,
                                           "Installed Version",
                                           gtk.CellRendererText(),
                                           text = 2)
        tree.insert_column_with_attributes(-1,
                                           "DB Version",
                                           gtk.CellRendererText(),
                                           text = 3)
        tree.insert_column_with_attributes(-1,
                                           "Repository",
                                           gtk.CellRendererText(),
                                           text = 4)

        col_num = 0
        for column in tree.get_columns():
            column.set_reorderable(True)
            column.set_resizable(True)
            column.set_clickable(True)
            column.set_sort_indicator(True)
            column.set_sort_column_id(col_num)
            col_num += 1
            continue
        return
    
    def _setup_dep_and_req_by_trees(self):

        dep_tree = self.gld.get_widget("dep_tree")
        req_tree = self.gld.get_widget("req_tree")
        self._setup_columns(dep_tree)
        self._setup_columns(req_tree)
        
    def _setup_icons(self, icons):
        for icon_name in icons.keys():
            icon = gtk.gdk.pixbuf_new_from_file(icons[icon_name])
            icon_set = gtk.IconSet(icon)
            icon_factory = gtk.IconFactory()
            icon_factory.add(icon_name, icon_set)
            icon_factory.add_default()
    
    def _setup_pac_columns(self, tree):
        tree.insert_column_with_attributes(-1,
                                           "",
                                           gtk.CellRendererPixbuf(),
                                           stock_id = 0)
        tree.insert_column_with_attributes(-1,
                                           "Package",
                                           gtk.CellRendererText(),
                                           text = 1)
        tree.insert_column_with_attributes(-1,
                                           "DB Version",
                                           gtk.CellRendererText(),
                                           text = 2)
        tree.insert_column_with_attributes(-1,
                                           "Installed Version",
                                           gtk.CellRendererText(),
                                           text = 3)
        col_num = 0
        for column in tree.get_columns():
            column.set_reorderable(True)
            column.set_resizable(True)
            column.set_clickable(True)
            column.set_sort_indicator(True)
            column.set_sort_column_id(col_num)
            col_num += 1
            continue
        return

    def _setup_tree(self, repo, notebook):
        
        tree = gtk.TreeView()
        tree.connect("cursor-changed", self.row_selected)
        tree.connect("row-activated", self.row_double_clicked)
        tree.set_rules_hint(True)
        self._setup_pac_columns(tree)

        scroll = gtk.ScrolledWindow(None, None)
        scroll.set_policy('automatic', 'automatic')
        scroll.add(tree)
        scroll.show_all()

        if repo == "third":
            label = "Thirds' packages"
        elif repo == "old":
            label = "Old packages"
        else:
            label = repo
            
        if repo == "old":
            notebook.prepend_page(scroll, gtk.Label(label))
        else:
            notebook.append_page(scroll, gtk.Label(label))

        self.trees[repo] = tree
    
    def _setup_trees(self):
        notebook = self.gld.get_widget("notebook")

        self.trees = {}

        for repo in self.db.repos:
            self._setup_tree(repo, notebook)
            continue

        self._setup_tree("third", notebook)
        return

    def _start_pulse(self):
        self.pulse = True
        thread.start_new_thread(self._do_pulse, ())
        return

    def _stop_pulse(self):
        self.pulse = False
        return

    def about(self, wid, event=None):
        return
    
    def add(self, wid, event=None):
        return

    def already(self, pack):
        self.statusbar.pop(self.cont_id)
        self.statusbar.push(self.cont_id, "Package %s already in cache. Using cache copy" %pack)
        return

    def down_cbk(self, pack, transfered, tot_size):
        percentile = transfered/tot_size

        gtk.threads_enter()
        self.prog_bar.show()
        self.statusbar.pop(self.cont_id)
        self.stausbar.push(self.cont_id, "Downloading %s" %pack)
        self.prog_bar.set_fraction(percentile)
        gtk.threads_leave()
        return        

    def err_cbk(self, string):
        dlg = gtk.MessageDialog(self.gld.get_widget("main_win"),
                                gtk.DIALOG_MODAL |
                                gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_ERROR,
                                gtk.BUTTONS_CLOSE,
                                string)
        dlg.run()
        dlg.destroy()
        return
    
    def hide(self, wid, event=None):
        return

    def md5sum_start(self, pack):
        self.statusbar.pop(self.cont_id)
        self.statusbar.push(self.cont_id, "Checking md5sum for %s" %pack)
        self.prog_bar.set_fraction(0.0)
        self._start_pulse()
        return

    def md5sum_stop(self):
        self._stop_pulse()
        return

    def old_packs(self, wid, event=None):
        if "old" not in self.trees.keys():
            self._setup_tree("old", self.gld.get_widget("notebook"))
            self.trees["old"].parent.hide()
            
        if wid.get_active():
            self.trees["old"].parent.show()
            self.gld.get_widget("notebook").set_current_page(0)
            thread.start_new_thread(self._set_old_model, ())
        else:
            self.trees["old"].parent.hide()
        return
    
    def pack_infos(self, wid, event=None):
        if wid.get_active():
            self.gld.get_widget("vpaned").show()
        else:
            self.gld.get_widget("vpaned").hide()
        return
    
    def preferences(self, wid, event=None):
        return

    def question(self, to_install):
        string = "Do you want to install these packages?: \n"
        for pac in to_install:
            string += "\t%s" %str(pac)
            continue
        dlg = gtk.MessageDialog(self.gld.get_widget("main_win"),
                                gtk.DIALOG_MODAL |
                                gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_YES_NO,
                                string)
        retcode = dlg.run()
        if retcode == gtk.RESPONSE_YES:
            dlg.destroy()
            return True
        else:
            dlg.destroy()
            return False

    def quit(self, wid, event=None):
        gtk.main_quit()
        return

    def refresh(self, wid, event=None):
        return

    def remove(self, wid, event=None):
        return

    def row_selected(self, wid, event=None):
        pac = self._get_selected_pac(wid)
        self.gld.get_widget("dep_tree").set_model(dep_model(pac, self.db))
        self.gld.get_widget("req_tree").set_model(req_model(pac, self.db))
        self._set_desc(pac)
        self._set_flist(pac)
        return
        
    def row_double_clicked(self, wid, event=None):
        return
    
    def run(self):

        gtk.threads_init()

        thread.start_new_thread(self._init_db, ())

        gtk.threads_enter()
        gtk.main()
        gtk.threads_leave()
        
    def sync(self, wid, event=None):
        n_book = self.gld.get_widget("notebook")
        num = n_book.get_current_page()
        scr = n_book.get_nth_page(num)
        tree = scr.get_child()
        (model, iter) = tree.get_selection().get_selected()
        if not iter:
            self.err_cbk("Select a package before clicking on sync button")
            return
        name = model.get_value(iter, 1)
        pack = self.db.get_by_name(name)
        self.pacman.sync_pack(pack)
        return

    def toolbar(self, wid, event=None):
        if wid.get_active():
            self.gld.get_widget("toolbar").show()
        else:
            self.gld.get_widget("toolbar").hide()
        return
    
    def upgrade(self, wid, event=None):
        return
    
    
                  

        
