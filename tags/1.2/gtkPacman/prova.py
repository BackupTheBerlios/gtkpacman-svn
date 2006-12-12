#!/usr/bin/env python

from Pacman import *

db = database()

db.set_olds()

for pac in db.get_olds():
	print "%s %s %s %s" %(pac.name, pac.version, pac.inst_ver, pac.coll)
