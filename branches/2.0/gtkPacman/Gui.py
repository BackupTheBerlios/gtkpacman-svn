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
        self._setup_icons(icons)

        self.stat_bar = self.gld.get_widget("statusbar")
        self.cont_id = self.stat_bar.get_context_id("statusbar")

        self.prog_bar = gtk.ProgressBar()
        self.stat_bar.pack_end(self.prog_bar, False, True, 0)


    def _init_db(self):
        self.db.setup_pacs()
        for repo in self.db.repos:
            self.trees[repo].set_model(pac_model(repo, self.db))
        self.trees["third"].set_model(pac_model("third", self.db))
        return

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

    def run(self):
        self._init_db()
        gtk.main()
        
    def sync(self, wid, event=None):
        return

    def upgrade(self, wid, event=None):
        return
    
    
                  

        
