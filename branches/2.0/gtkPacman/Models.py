import gtk

class pac_model(gtk.ListStore):

    def __init__(self, repo, db):

        gtk.ListStore.__init__(self, str, str, str, str)

        for pac in db[repo].values():
            if type(pac) != type(list()):
                raise TypeError, "pac isn't a list"

            if len(pac) == 7:
                image = "green"
                db_ver = pac[4]
                inst_ver = pac[0][1]
                if pac[6]:
                    image = "yellow"
                    
            else:
                image = "red"
                inst_ver = "-"
                db_ver = pac[0][1]

            name = pac[0][0]
            self.append([image, name, db_ver, inst_ver])

class dep_model(gtk.ListStore):

    def __init__(self, pac, db):

        gtk.ListStore.__init__(self, str, str, str, str, str)

        for dep in pac[1]:

            dep_pac = db.get_by_name(dep)

            if not dep_pac:
                self.append([None, dep, None, None, None])
                continue
            
            if len(dep_pac) == 7:
                db_ver = dep_pac[4]
                inst_ver = dep_pac[0][1]
                repo = dep_pac[5]
                if dep_pac[6]:
                    image = "yellow"
                else:
                    image = "green"
            else:
                db_ver = dep_pac[0][1]
                inst_ver = "-"
                image = "red"
                repo = dep_pac[2]
                
            name = dep_pac[0][0]
                    
            self.append([image, name, inst_ver, db_ver, repo])
        
class req_model(gtk.ListStore):

    def __init__(self, pac, db):

        gtk.ListStore.__init__(self, str, str, str, str, str)

        if len(pac) < 7:
            return

        for req in pac[2]:

            req_pac = db.get_by_name(req)
            if not req_pac:
                self.append([None, req, None, None, None])
                continue
            
            if len(req_pac) == 7:
                db_ver = req_pac[4]
                inst_ver = req_pac[0][1]
                repo = req_pac[5]
                if req_pac[6]:
                    image = "yellow"
                else:
                    image = "green"
            else:
                db_ver = req_pac[0][1]
                inst_ver = "-"
                repo = req_pac[2]
                image = "red"

            name = req_pac[0][0]

            self.append([image, name, inst_ver, db_ver, repo])
