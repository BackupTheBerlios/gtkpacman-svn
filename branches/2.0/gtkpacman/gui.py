from gtk.glade import XML
from gtk import ListStore, TreeStore, TreeView, TreeViewColumn
from gtk import CellRendererText, CellRendererPixbuf, CellRendererToggle
from gtk import ScrolledWindow, Label
from gtk import STOCK_ADD, STOCK_GO_UP, STOCK_REMOVE
from gtk import  main_quit

import pacman

class gui:

    def __init__(self, fname, icons):
        """Create the XML Object and connect handlers, then setup notebook"""
        self.gld = XML(fname, "main_win")

        hand_dict = { "quit": self.quit, 
                      "add_install": self.add_install,
                      "remove_install": self.remove_install,
                      "add_remove": self.add_remove,
                      "remove_remove": self.remove_remove,
                      "execute": self.execute,
                      #up_sys: self.up_sys,
                      #refr_db: self.refr_db,
                      #add_local: self.add_local,
                      #clear_cache: self.clear_cache,
                      #empty_cache: self.empty_cache,
                      #about: self.about,
                      "repo_changed": self.change_repo}

        self.gld.signal_autoconnect(hand_dict)

        self.packages = pacman.get_all()
        self.queues = {"install": [], "remove": []}
        self.queued = {}
        
        self._set_icons(icons)
        self._setup_notebook()

        self._setup_repos_tree()
        
        self.gld.get_widget("main_win").show_all()

    def _set_icons(self, icons):
        import gtk.gdk
        """Set stock icons for the app"""
        for icon_name in icons.keys():
            icon = gtk.gdk.pixbuf_new_from_file(icons[icon_name])
            icon_set = gtk.IconSet(icon)
            icon_factory = gtk.IconFactory()
            icon_factory.add(icon_name, icon_set)
            icon_factory.add_default()
            continue
        return
    
    def _setup_notebook(self):
        """Setup the notebook"""
        notebook = self.gld.get_widget("notebook")

        self.pages = {"remote": {}, "local": {}}

        self.pages["all"] = notebook_page(self.packages)
        notebook.append_page(self.pages["all"], Label("All"))

        self.pages["remote"]["node"] = self.pages["all"]
        
        self.pages["local"]["node"]= notebook_page(self.packages, node="local")
        notebook.append_page(self.pages["local"]["node"], Label("local"))
        
        for repo in pacman.repos:
            self.pages["remote"][repo] = notebook_page(self.packages, repo,
                                                       "remote")
            notebook.append_page(self.pages["remote"][repo], Label(repo))

            self.pages["local"][repo] = notebook_page(self.packages, repo,
                                                      "local")
            notebook.append_page(self.pages["local"][repo], Label(repo))
            continue

        self.pages["local"]["none"] = notebook_page(self.packages, "none",
                                                    "local")
        notebook.append_page(self.pages["local"]["none"], Label("none"))
        return

    def _setup_repos_tree(self):
        """Setup the repos tree"""
        tree = self.gld.get_widget("treeview")

        tree.insert_column_with_attributes(-1, "", CellRendererText(), text=0)

        model = TreeStore(str)

        parent = model.append(None, ["All"])
        for node in self.packages.keys():
            nodes = {"local": "Installed", "remote": "Database Entries"}
            node_it = model.append(parent, [nodes[node]])
            for repo in self.packages[node].keys():
                model.append(node_it, [repo])
                continue
            continue
        tree.set_model(model)
        return

    def _get_selected_page(self, repo_tree, toggle=None):        
        model, tree_iter = repo_tree.get_selection().get_selected()
        if tree_iter is None:
            tree_iter = model.get_iter_from_string("0")

        selected = model.get_value(tree_iter, 0)
        depth = model.iter_depth(tree_iter)
        nodes = {"Installed": "local", "Database Entries": "remote"}

        if depth is 0:
            page = self.pages["all"]
        elif depth is 1:
            page = self.pages[nodes[selected]]["node"]
        elif depth > 1:
            node_iter = model.iter_parent(tree_iter)
            node = model.get_value(node_iter, 0)
            page = self.pages[nodes[node]][selected]
        return page

    def change_repo(self, widget, data=None):
        notebook = self.gld.get_widget("notebook")
        
        page = self._get_selected_page(widget)    
        page_num = notebook.page_num(page)
        notebook.set_current_page(page_num)
        return

    def add_install(self, widget=None, data=None):
        repos_tree = self.gld.get_widget("treeview")
        page = self._get_selected_page(repos_tree)

        model, l_iter = page.tree.get_selection().get_selected()
        name = model.get_value(l_iter, 2)

        if name not in self.queues["install"]:
            if name in self.queues["remove"]:
                self.queues["remove"].remove(name)
                
            self.queues["install"].append(name)
            installed = model.get_value(l_iter, 0)
            if installed == "yellow" or installed == "green":
                model.set_value(l_iter, 1, STOCK_GO_UP)
            else:
                model.set_value(l_iter, 1, STOCK_ADD)
            self.queued[name] = (model, l_iter)
        return

    def remove_install(self, widget=None, data=None):
        repos_tree = self.gld.get_widget("treeview")
        page = self._get_selected_page(repos_tree)

        model, l_iter = page.tree.get_selection().get_selected()
        name = model.get_value(l_iter, 2)
        
        if name in self.queues["install"]:
            self.queues["install"].remove(name)
            model.set_value(l_iter, 1, "")
            self.queued.pop(name)
        return

    def add_remove(self, widget=None, data=None):
        repos_tree = self.gld.get_widget("treeview")
        page = self._get_selected_page(repos_tree)

        model, l_iter = page.tree.get_selection().get_selected()
        name = model.get_value(l_iter, 2)
        
        if name not in self.queues["remove"]:
            if name in self.queues["install"]:
                self.queues["install"].remove(name)
                
            self.queues["remove"].append(name)
            model.set_value(l_iter, 1, STOCK_REMOVE)
            self.queued[name] = (model, l_iter)
        return

    def remove_remove(self, widget=None, data=None):
        repos_tree = self.gld.get_widget("treeview")
        page = self._get_selected_page(repos_tree)

        model, l_iter = page.tree.get_selection().get_selected()
        name = model.get_value(l_iter, 2)

        if name in self.queues["remove"]:
            self.queues["remove"].remove(name)
            model.set_value(l_iter, 1, "")
        return

    def execute(self, widget, data=None):
        for k in self.queues.keys():
            print k
            for name in self.queues[k]:
                print "\t"+name
                self.queued[name][0].set_value(self.queued[name][1], 1, "")
                continue
            self.queues[k] = []
            continue
        return
        
    def quit(self, widget, event=None, data=None):
        main_quit()
        
class notebook_page(ScrolledWindow):

    def __init__(self, packages, repo=None, node=None):
        
        ScrolledWindow.__init__(self, None, None)
        self.set_policy("automatic", "automatic")

        self.tree = TreeView()
        self.tree.set_model(pac_list(packages, repo, node))
        self._setup_columns()

        self.add(self.tree)
        self.show_all()

    def _setup_columns(self):

        pixbuf_renderer = CellRendererPixbuf()
        action_renderer = CellRendererPixbuf()

        first_col = TreeViewColumn()
        first_col.pack_start(pixbuf_renderer)
        first_col.pack_start(action_renderer)
        first_col.set_attributes(pixbuf_renderer, stock_id=0)
        first_col.set_attributes(action_renderer, stock_id=1)
        self.tree.insert_column(first_col, -1)
        
        self.tree.insert_column_with_attributes(-1,
                                                "Name",
                                                CellRendererText(),
                                                text=2)
        self.tree.insert_column_with_attributes(-1,
                                                "Version",
                                                CellRendererText(),
                                                text=3)
        self.tree.insert_column_with_attributes(-1,
                                                "Repo",
                                                CellRendererText(),
                                                text=4)
        for num in range(4):
            col = self.tree.get_column(num)
            col.set_resizable(True)
            col.set_clickable(True)
            col.set_sort_indicator(True)
            col.set_reorderable(True)
            col.set_sort_column_id(num+1)
            continue

class pac_list(ListStore):

    def __init__(self, packages, repo, node):

        ListStore.__init__(self, str, str, str, str, str)

        self.packages = packages
        
        if not (node or repo):
            self._list_all()
        elif not repo:            
            self._list_node(node)
        else:
            self._list_repo(node, repo)

    def _list_all(self):
        for node in ["local", "remote"]:
            self._list_node(node, True)
            continue
        return

    def _list_node(self, node, all=False):
            for repo in self.packages[node].keys():
                self._list_repo(node, repo, all)
                continue
            return

    def _list_repo(self, node, repo, all=False):
        l_names = self.packages["local"][repo].keys()
        for name in self.packages[node][repo].keys():
            if all and node is not "remote" and name in l_names:
                continue
            
            version = self.packages[node][repo][name]["version"]
            
            if node is "local" and repo is not "none":
                rem_ver = self.packages["remote"][repo][name][
                    "version"]
                if version < rem_ver:
                    image = "yellow"     
                else:
                    image = "green"
            else:
                if name in self.packages["local"][repo].keys():
                    loc_ver = self.packages["local"][repo][name][
                        "version"]
                    if loc_ver < version:
                        image = "yellow"
                    else:
                        image = "green"
                else:
                    image = "red"
            self.append([image, "", name, version, repo])
            continue
        return
