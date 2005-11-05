import gtk

class pac_model(gtk.ListStore):

    def __init__(self, repo, db):

        gtk.ListStore.__init__(self, str, str, str, str)

        for pac in db[repo].values():
            if type(pac) != type(list()):
                raise TypeError, "pac isn't a list"

            if len(pac) > 2:
                image = gtk.STOCK_YES
                db_ver = pac[4]
                inst_ver = pac[0][1]
            else:
                image = gtk.STOCK_NO
                inst_ver = "-"
                db_ver = pac[0][1]

            name = pac[0][0]
            self.append([image, name, db_ver, inst_ver])
