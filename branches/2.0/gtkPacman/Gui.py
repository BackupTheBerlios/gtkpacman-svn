import gtk, gtk.glade

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
                  'remove' : self.remove }
        self.gld.signal_autoconnect(hands)

        self.db = database()

        self._setup_trees()
        self._setup_dep_and_req_by_trees()
        self._setup_icons(icons)

        self.stat_bar = self.gld.get_widget("statusbar")
        self.cont_id = self.stat_bar.get_context_id("statusbar")

        self.prog_bar = gtk.ProgressBar()
        self.stat_bar.pack_end(self.prog_bar, False, True, 0)


    def _get_selected_pac(self, tree):
        (model, treeiter) = tree.get_selection().get_selected()
        name = model.get_value(treeiter, 1)
        pac = self.db.get_by_name(name)
        return pac
            
    def _init_db(self):
        self.db.setup_pacs()
        for repo in self.db.repos:
            self.trees[repo].set_model(pac_model(repo, self.db))
        self.trees["third"].set_model(pac_model("third", self.db))
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
    
    def _setup_trees(self):
        notebook = self.gld.get_widget("notebook")

        self.trees = {}

        for repo in self.db.repos:
            tree = gtk.TreeView()
            tree.connect("cursor-changed", self.row_selected)
            tree.connect("row-activated", self.row_double_clicked)
            tree.set_rules_hint(True)
            self._setup_pac_columns(tree)
            scroll = gtk.ScrolledWindow(None, None)
            scroll.set_policy('automatic', 'automatic')
            scroll.add(tree)
            scroll.show_all()
            notebook.append_page(scroll, gtk.Label(repo))
            self.trees[repo] = tree
            continue

        tree = gtk.TreeView()
        tree.set_rules_hint(True)
        self._setup_pac_columns(tree)
        scroll = gtk.ScrolledWindow(None, None)
        scroll.set_policy('automatic', 'automatic')
        scroll.add(tree)
        scroll.show_all()
        notebook.append_page(scroll, gtk.Label("Thirds' packages"))
        self.trees["third"] = tree                             
        return

    def about(self, wid, event=None):
        return
    
    def add(self, wid, event=None):
        return

    def hide(self, wid, event=None):
        return
    
    def preferences(self, wid, event=None):
        return

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
        self._init_db()
        gtk.main()
        
    def sync(self, wid, event=None):
        return

    def upgrade(self, wid, event=None):
        return
    
    
                  

        
